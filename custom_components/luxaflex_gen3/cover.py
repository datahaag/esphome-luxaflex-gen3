"""Cover entities for Luxaflex Gen 3 shades."""

import logging
from typing import Any

from homeassistant.components.cover import CoverDeviceClass, CoverEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .ble_client import LuxaflexBLEClient
from .const import (
    CONF_BLE_TIMEOUT,
    CONF_ENCRYPTION_KEY,
    CONF_MAC_ADDRESS,
    CONF_SCAN_INTERVAL,
    DOMAIN,
)
from .entity import LuxaflexGen3Entity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Luxaflex Gen 3 cover from a config entry."""
    mac_address = entry.data[CONF_MAC_ADDRESS]
    name = entry.data["name"]
    encryption_key = entry.data.get(CONF_ENCRYPTION_KEY)
    ble_timeout = entry.data.get(CONF_BLE_TIMEOUT, 6)
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, 15)

    client = LuxaflexBLEClient(mac_address, encryption_key)
    
    async_add_entities(
        [LuxaflexGen3Cover(client, name, mac_address, ble_timeout, scan_interval)]
    )


class LuxaflexGen3Cover(LuxaflexGen3Entity, CoverEntity):
    """Representation of a Luxaflex Gen 3 shade."""

    def __init__(self, client, name, mac_address, ble_timeout, scan_interval):
        """Initialize the cover."""
        super().__init__(None, mac_address, name)
        self._client = client
        self._ble_timeout = ble_timeout
        self._scan_interval = scan_interval
        self._attr_device_class = CoverDeviceClass.BLIND
        self._attr_supported_features = (
            CoverEntity.Feature.OPEN
            | CoverEntity.Feature.CLOSE
            | CoverEntity.Feature.STOP
            | CoverEntity.Feature.SET_POSITION
        )
        self._current_position = None
        self._is_closed = None

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the cover."""
        if await self._connect_and_execute(self._client.close):
            self._is_closed = True
            self._current_position = 0

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        if await self._connect_and_execute(self._client.open):
            self._is_closed = False
            self._current_position = 100

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover."""
        await self._connect_and_execute(self._client.stop)

    async def async_set_cover_position(self, position: int, **kwargs: Any) -> None:
        """Set the cover position."""
        if await self._connect_and_execute(
            lambda: self._client.set_position(position)
        ):
            self._current_position = position
            self._is_closed = position == 0

    async def _connect_and_execute(self, command_func) -> bool:
        """Connect to device, execute command, and disconnect."""
        try:
            if not self._client.is_connected():
                if not await self._client.connect(timeout=self._ble_timeout):
                    return False
            
            result = await command_func()
            await self._client.disconnect()
            return result
        except Exception as err:
            _LOGGER.error("Error executing command: %s", err)
            await self._client.disconnect()
            return False

    @property
    def current_cover_position(self) -> int | None:
        """Return the current position of the cover."""
        return self._current_position

    @property
    def is_closed(self) -> bool | None:
        """Return if the cover is closed."""
        return self._is_closed
