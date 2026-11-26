"""Verified on/off states from the DD20."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import DreameDehumConfigEntry, DreameDehumCoordinator
from .entity import DreameDehumEntity
from .profiles import Kind

PARALLEL_UPDATES = 0

_DEVICE_CLASSES = {
    "timer_on": BinarySensorDeviceClass.RUNNING,
    "air_drying": BinarySensorDeviceClass.RUNNING,
}


async def async_setup_entry(
    hass: HomeAssistant, entry: DreameDehumConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    """Add a binary sensor for each yes/no property."""
    coordinator = entry.runtime_data
    async_add_entities(
        DreameDehumBinarySensor(coordinator, prop.key)
        for prop in coordinator.device.profile.of_kind(Kind.BINARY_SENSOR)
    )


class DreameDehumBinarySensor(DreameDehumEntity, BinarySensorEntity):
    """One yes/no state."""

    def __init__(self, coordinator: DreameDehumCoordinator, key: str) -> None:
        super().__init__(coordinator, key)
        self._attr_device_class = _DEVICE_CLASSES.get(key)

    @property
    def is_on(self) -> bool | None:
        value = self.raw_value
        if not isinstance(value, (int, bool)) or value not in (0, 1):
            return None
        return bool(value)
