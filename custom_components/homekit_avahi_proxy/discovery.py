"""Launch a Zeroconf browser for HomeKit Bridge instances and translate them to Avahi."""
import logging
import re
import os
from zeroconf import ServiceListener, ServiceBrowser, Zeroconf, ServiceInfo
import xml.etree.cElementTree as ET

from homeassistant.core import HomeAssistant
from homeassistant.const import EVENT_HOMEASSISTANT_STOP

from .const import AVAHI_TYPE
from .helpers import HomeKitBridgeZeroconf

_LOGGER = logging.getLogger(__name__)


def service_file_path(path: str, service_name: str) -> str:
    suffixless_name = service_name.removesuffix(f'.{AVAHI_TYPE}')
    sanitized_name = re.sub(r"[ /\\?%*:|\"<>\x7F\x00-\x1F]", "_", suffixless_name)
    file_name = f'{sanitized_name}.service'
    return f'{path}/{file_name}'


def add_homekit_avahi_proxy(path: str, service_info: ServiceInfo) -> None:
    """When discovering a HomeKit Bridge, write the translated Avahi XML to the target file."""
    service_group = ET.Element("service-group")
    ET.SubElement(service_group, "name").text = service_info.name
    service = ET.SubElement(service_group, "service")
    ET.SubElement(service, "type").text = service_info.type.removesuffix('local.')
    ET.SubElement(service, "port").text = str(service_info.port)
    for property_key, property_value in service_info.properties.items():
        ET.SubElement(service, "txt-record").text = f"{property_key.decode('utf-8')}={property_value.decode('utf-8')}"

    tree = ET.ElementTree(service_group)
    file_path = service_file_path(path, service_info.name)
    tree.write(file_path)
    _LOGGER.info(f'Written {os.path.getsize(file_path)} bytes to {file_path}')


def _remove_homekit_avahi_proxy(path: str, name: str) -> None:
    # Removed HomeKit Bridge
    file_path = service_file_path(path, name)
    try:
        os.remove(file_path)
        _LOGGER.info(f'Removed {file_path}')
    except FileNotFoundError:
        _LOGGER.warning(f'Avahi file for deleted HomeKit Bridge service \
                         "{name}" at {file_path} did not exist.')
        pass


def setup_internal_discovery(hass: HomeAssistant, path: str) -> None:
    """Set up the HomeKit Bridge internal discovery."""
    class HomeKitBridgeListener(ServiceListener):
        def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
            info = zc.get_service_info(type_, name)
            _LOGGER.debug(f'HomeKit Bridge {name} added, service info: {info}')
            add_homekit_avahi_proxy(path, info)

        def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
            info = zc.get_service_info(type_, name)
            _LOGGER.debug(f'HomeKit Bridge {name} updated, service info: {info}')
            add_homekit_avahi_proxy(path, info)

        def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
            _LOGGER.debug(f'HomeKit Bridge {name} removed')
            _remove_homekit_avahi_proxy(path, name)

    _LOGGER.debug("Starting internal HomeKit Bridge discovery")
    zeroconf = HomeKitBridgeZeroconf.get_zeroconf()
    listener = HomeKitBridgeListener()
    browser = ServiceBrowser(zeroconf, AVAHI_TYPE, listener)

    def stop_discovery(event):
        """Stop discovery of new HomeKit Bridges."""
        _LOGGER.debug("Stopping internal HomeKit Bridge discovery")
        browser.cancel()

    hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, stop_discovery)
