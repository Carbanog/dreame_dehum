"""Model profiles: what each Dreame dehumidifier can be asked to do.

A profile is pure data. The device layer (device.py) refuses any read or write
the profile doesn't declare, so a wrong guess about one model can't reach
another. To add a model, map it with tools/probe.py and add a Profile to
PROFILES.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Status(StrEnum):
    """How much of a profile has been confirmed on a real device."""

    VERIFIED = "verified"  # reads and writes confirmed on a real unit
    MAPPED = "mapped"  # reads confirmed on a real unit; writes not yet


class Kind(StrEnum):
    """Which platform shows a property."""

    POWER = "power"
    MODE = "mode"
    TARGET_HUMIDITY = "target_humidity"
    HUMIDITY = "humidity"
    SENSOR = "sensor"
    BINARY_SENSOR = "binary_sensor"
    SWITCH = "switch"
    SELECT = "select"
    INFO = "info"  # device registry only, no entity
    NUMBER = "number"
    UNKNOWN = "unknown"  # read but not understood yet; shown as a raw diagnostic


@dataclass(frozen=True, slots=True)
class Prop:
    """One MIoT property.

    values: allowed write values; None means the property is read-only.
    options: value -> option key, for enum-like properties (translated).
    """

    key: str
    siid: int
    piid: int
    kind: Kind
    values: frozenset[int] | None = None
    options: dict[int, str] | None = None

    @property
    def address(self) -> tuple[int, int]:
        return (self.siid, self.piid)

    @property
    def writable(self) -> bool:
        return self.values is not None


@dataclass(frozen=True, slots=True)
class Profile:
    """Everything the integration may do with one model.

    power_on / power_off: the values of the power property.
    manual_mode: the mode in which the fan speed can be set.
    """

    model: str
    name: str
    status: Status
    props: tuple[Prop, ...]
    power_on: int = 1
    power_off: int = 2
    manual_mode: int | None = None
    humidity_step: int = 1

    def prop(self, key: str) -> Prop | None:
        return next((p for p in self.props if p.key == key), None)

    def of_kind(self, kind: Kind) -> tuple[Prop, ...]:
        return tuple(p for p in self.props if p.kind is kind)


DD20_AUTO, DD20_SLEEP, DD20_DRY, DD20_CUSTOM = 0, 1, 2, 3
_DD20_POWER_ON, _DD20_POWER_OFF, _DD20_PREHEATING = 1, 2, 3

# The lab polls addresses checked against the app or the upstream DD20 profile.
DD20 = Profile(
    model="dreame.dehum.u2512",
    name="DD20",
    status=Status.MAPPED,
    props=(
        Prop(
            "power",
            2,
            1,
            Kind.BINARY_SENSOR,
            options={_DD20_POWER_OFF: "off", _DD20_PREHEATING: "preheating", _DD20_POWER_ON: "on"},
        ),
        Prop(
            "mode",
            2,
            3,
            Kind.MODE,
            options={DD20_AUTO: "auto", DD20_SLEEP: "sleep", DD20_DRY: "dry", DD20_CUSTOM: "custom"},
        ),
        Prop("fan_speed", 2, 4, Kind.SELECT, options={0: "low", 1: "high"}),
        Prop("target_humidity", 2, 5, Kind.TARGET_HUMIDITY),
        Prop("auto_air_dry", 2, 6, Kind.BINARY_SENSOR),
        Prop("air_drying", 2, 10, Kind.BINARY_SENSOR),
        Prop("humidity", 3, 2, Kind.HUMIDITY),
        Prop("key_tone", 4, 1, Kind.BINARY_SENSOR),
        Prop("child_lock", 5, 1, Kind.BINARY_SENSOR),
        Prop("timer_on", 7, 1, Kind.BINARY_SENSOR),
        Prop("timer_hours", 7, 2, Kind.NUMBER),
        Prop("plasma", 7, 6, Kind.BINARY_SENSOR),
        Prop("swing", 7, 7, Kind.BINARY_SENSOR),
    ),
    power_on=_DD20_POWER_ON,
    power_off=_DD20_POWER_OFF,
    manual_mode=DD20_CUSTOM,
    humidity_step=5,
)

PROFILES: tuple[Profile, ...] = (DD20,)


def get_profile(model: str) -> Profile | None:
    """Return the profile for a model ID, or None if it isn't supported."""
    return next((p for p in PROFILES if p.model == model), None)
