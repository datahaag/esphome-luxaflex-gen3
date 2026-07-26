"""Base entity for Luxaflex Gen 3."""

from homeassistant.helpers.entity import DeviceInfo, Entity

from .const import DOMAIN


class LuxaflexGen3Entity(Entity):
    """Base class for Luxaflex Gen 3 entities."""

    def __init__(self, mac_address, name):
        """Initialize the entity."""
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{mac_address}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, mac_address)},
            name=name,
            manufacturer="Luxaflex (Hunter Douglas)",
            model="PowerView Gen 3",
        )
