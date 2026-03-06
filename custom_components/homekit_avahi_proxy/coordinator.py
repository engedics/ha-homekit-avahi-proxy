"""Coordinator for HomeKit Avahi Proxy."""
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.components.zeroconf import async_get_instance

from .const import NAME
from .discovery import setup_internal_discovery
from .helpers import HomeKitBridgeZeroconf

_LOGGER = logging.getLogger(__name__)


class HomeKitBridgeAvahiProxyCoordinator(DataUpdateCoordinator):
    """Coordinator that runs once on initialization."""

    def __init__(self, hass, path):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=NAME,
            update_interval=None,
        )
        self.path = path

    async def _async_update_data(self):
        """Run initialization code."""
        _LOGGER.debug('Running initialization with target path: %s', self.path)
        HomeKitBridgeZeroconf.set_zeroconf(await async_get_instance(self.hass))
        self.hass.async_add_executor_job(setup_internal_discovery, self.hass, self.path)
        _LOGGER.debug('Component initialized')
        return {}
