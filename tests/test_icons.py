"""Every mode and entity key has an icon."""

from __future__ import annotations

import json
from pathlib import Path

from custom_components.dreame_dehum.profiles import PROFILES, Kind

ICONS = json.loads((Path(__file__).parents[1] / "custom_components/dreame_dehum/icons.json").read_text())["entity"]


def test_every_mode_has_an_icon() -> None:
    mode_icons = ICONS["sensor"]["mode"]["state"]
    for profile in PROFILES:
        mode = profile.prop("mode")
        assert mode and mode.options
        assert set(mode.options.values()) <= set(mode_icons)


def test_every_read_only_entity_has_an_icon() -> None:
    for profile in PROFILES:
        for prop in profile.props:
            platform = "binary_sensor" if prop.kind is Kind.BINARY_SENSOR else "sensor"
            assert prop.key in ICONS[platform], prop.key
            assert not prop.writable
