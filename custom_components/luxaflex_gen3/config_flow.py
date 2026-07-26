"""Config flow for Luxaflex Gen 3 integration."""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_BLE_TIMEOUT,
    CONF_ENCRYPTION_KEY,
    CONF_MAC_ADDRESS,
    CONF_SCAN_INTERVAL,
    DEFAULT_BLE_TIMEOUT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)


def validate_mac_address(mac: str) -> str:
    """Validate MAC address format."""
    import re
    mac_pattern = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")
    if not mac_pattern.match(mac):
        raise vol.Invalid("Invalid MAC address format")
    return mac


def validate_encryption_key(key: str) -> str:
    """Validate encryption key format."""
    import re
    key_pattern = re.compile(r"^[0-9a-fA-F]{32}$")
    if not key_pattern.match(key):
        raise vol.Invalid("Encryption key must be 32 hexadecimal characters")
    return key


STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): str,
        vol.Required(CONF_MAC_ADDRESS): str,
        vol.Optional(CONF_ENCRYPTION_KEY): str,
        vol.Optional(CONF_BLE_TIMEOUT, default=DEFAULT_BLE_TIMEOUT): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=30)
        ),
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=5, max=300)
        ),
    }
)


class LuxaflexGen3ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Luxaflex Gen 3."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                validate_mac_address(user_input[CONF_MAC_ADDRESS])
                if user_input.get(CONF_ENCRYPTION_KEY):
                    validate_encryption_key(user_input[CONF_ENCRYPTION_KEY])
            except vol.Invalid as exc:
                errors[exc.path[0]] = exc.msg

            if not errors:
                await self.async_set_unique_id(user_input[CONF_MAC_ADDRESS])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
