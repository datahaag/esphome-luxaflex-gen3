"""Config flow for Luxaflex Gen 3 integration."""

import asyncio
import voluptuous as vol
from bleak import BleakScanner
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import (
    BLE_NAME_PREFIXES,
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

    def __init__(self):
        """Initialize the config flow."""
        self._discovered_devices = []

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

    async def async_step_discovery(
        self, user_input: dict[str, any] | None = None
    ) -> FlowResult:
        """Handle the discovery step."""
        if user_input is not None:
            # User selected devices to add
            selected_devices = user_input.get("devices", [])
            for device in selected_devices:
                await self.async_set_unique_id(device["address"])
                self._abort_if_unique_id_configured()
                
                # Create entry for each selected device
                self.hass.config_entries.async_add_entry(
                    config_entries.ConfigEntry(
                        version=self.VERSION,
                        domain=DOMAIN,
                        title=device["name"],
                        data={
                            CONF_NAME: device["name"],
                            CONF_MAC_ADDRESS: device["address"],
                            CONF_ENCRYPTION_KEY: None,  # No encryption key for auto-discovered devices
                            CONF_BLE_TIMEOUT: DEFAULT_BLE_TIMEOUT,
                            CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
                        },
                        source="discovery",
                    )
                )
            
            return self.async_create_entry(title="Luxaflex Gen 3 Discovery", data={})

        # Scan for BLE devices
        try:
            devices = await BleakScanner.discover(timeout=10.0)
            self._discovered_devices = [
                {
                    "name": device.name or "Unknown",
                    "address": device.address,
                }
                for device in devices
                if device.name
                and any(device.name.startswith(prefix) for prefix in BLE_NAME_PREFIXES)
            ]
        except Exception as err:
            return self.async_show_form(
                step_id="discovery",
                errors={"base": "discovery_failed"},
                description_placeholders={"error": str(err)},
            )

        if not self._discovered_devices:
            return self.async_show_form(
                step_id="discovery",
                errors={"base": "no_devices_found"},
            )

        # Show discovered devices
        devices_schema = vol.Schema(
            {
                vol.Required(
                    "devices",
                    default=[],
                ): vol.All(
                    [vol.In(self._discovered_devices)],
                )
            }
        )

        return self.async_show_form(
            step_id="discovery",
            data_schema=devices_schema,
        )
