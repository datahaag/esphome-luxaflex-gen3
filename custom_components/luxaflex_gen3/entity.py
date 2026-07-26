"""Base entity for Luxaflex Gen 3."""

from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


class LuxaflexGen3Entity(CoordinatorEntity, Entity):
    """Base class for Luxaflex Gen 3 entities."""

    def __init__(self, coordinator, mac_address, name):
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{mac_address}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, mac_address)},
            name=name,
            manufacturer="Luxaflex (Hunter Douglas)",
            model="PowerView Gen 3",
        )
