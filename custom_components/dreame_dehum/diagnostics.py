"""Diagnostics with only the exact, known model and profile status."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from .const import CONF_MODEL
from .coordinator import DreameDehumConfigEntry
from .profiles import get_profile


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: DreameDehumConfigEntry) -> dict[str, Any]:
    """Return diagnostics for one dehumidifier."""
    profile = get_profile(entry.data[CONF_MODEL])
    return {
        "profile": {"model": profile.model, "status": profile.status.value} if profile else None,
    }
