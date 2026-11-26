"""Verified on/off states from the DD20."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import DreameDehumConfigEntry, DreameDehumCoordinator
from .entity import DreameDehumEntity
from .profiles import Kind, Prop

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
        DreameDehumBinarySensor(coordinator, prop)
        for prop in coordinator.device.profile.of_kind(Kind.BINARY_SENSOR)
    )


class DreameDehumBinarySensor(DreameDehumEntity, BinarySensorEntity):
    """One yes/no state."""

    def __init__(self, coordinator: DreameDehumCoordinator, prop: Prop) -> None:
        super().__init__(coordinator, prop.key)
        self._attr_device_class = _DEVICE_CLASSES.get(prop.key)
        self._power_states = prop.options if prop.key == "power" else None

    @property
    def is_on(self) -> bool | None:
        value = self.raw_value
        if self._power_states is not None:
            state = self._power_states.get(value) if type(value) is int else None
            return state != "off" if state is not None else None
        if not isinstance(value, (int, bool)) or value not in (0, 1):
            return None
        return bool(value)
