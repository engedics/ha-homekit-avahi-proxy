"""Config flow for HomeKit Avahi Proxy."""
import logging
import os
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_PATH
from homeassistant.exceptions import ConfigEntryError

from .const import DOMAIN, NAME

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PATH, default='/etc/avahi/services'): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    path = data[CONF_PATH]

    # Check file path existence/writability
    if not os.path.exists(path):
        raise PathNotFound
    if not os.path.isdir(path):
        raise PathNotDirectory
    if not os.access(path, os.W_OK):
        raise PathNotWritable

    # Return info that you want to store in the config entry.
    return {
        "title": NAME,
        "data": {CONF_PATH: path},
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                await validate_input(self.hass, user_input)
            except PathNotFound:
                errors["base"] = 'not_found'
            except PathNotDirectory:
                errors["base"] = 'not_directory'
            except PathNotWritable:
                errors["base"] = 'not_writable'
            except Exception as e:  # pylint: disable=broad-except
                _LOGGER.exception(e)
                errors["base"] = 'unknown'
            else:
                return self.async_create_entry(
                    title=NAME,
                    data=user_input
                )

        return self.async_show_form(
            step_id='user',
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors
        )


class PathNotFound(ConfigEntryError):
    """Error to indicate the target file does not exist."""


class PathNotDirectory(ConfigEntryError):
    """Error to indicate the target file does not exist."""


class PathNotWritable(ConfigEntryError):
    """Error to indicate the target file is not writable."""
