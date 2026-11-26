"""Read-only, typed DD20 measurements and modes."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import DreameDehumConfigEntry, DreameDehumCoordinator
from .entity import DreameDehumEntity
from .profiles import Prop

PARALLEL_UPDATES = 0

DESCRIPTIONS = {
    "humidity": SensorEntityDescription(
        key="humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "target_humidity": SensorEntityDescription(
        key="target_humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
    ),
    "timer_hours": SensorEntityDescription(
        key="timer_hours",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.HOURS,
    ),
}


async def async_setup_entry(
    hass: HomeAssistant, entry: DreameDehumConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    """Expose verified readings as sensors, with no control services."""
    coordinator = entry.runtime_data
    async_add_entities(
        DreameDehumSensor(coordinator, prop)
        for prop in coordinator.device.profile.props
        if prop.key in DESCRIPTIONS or prop.options
    )


class DreameDehumSensor(DreameDehumEntity, SensorEntity):
    """Report a numeric measurement or a translated mode."""

    def __init__(self, coordinator: DreameDehumCoordinator, prop: Prop) -> None:
        super().__init__(coordinator, prop.key)
        self._options = prop.options
        if self._options:
            self.entity_description = SensorEntityDescription(
                key=prop.key, device_class=SensorDeviceClass.ENUM, options=list(self._options.values())
            )
        else:
            self.entity_description = DESCRIPTIONS[prop.key]

    @property
    def native_value(self) -> float | str | None:
        value = self.raw_value
        if self._options:
            return self._options.get(value) if type(value) is int else None
        maximum = 12 if self.entity_description.key == "timer_hours" else 100
        return (
            value if isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= maximum else None
        )
