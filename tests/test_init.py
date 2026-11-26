"""Setup, entities and commands against a fake cloud."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er, issue_registry as ir

from custom_components.dreame_dehum.api import AuthFailed, CannotConnect
from custom_components.dreame_dehum.const import DOMAIN, MAX_FAILED_POLLS
from custom_components.dreame_dehum.diagnostics import async_get_config_entry_diagnostics

from .conftest import FakeCloud, make_entry

HUMIDITY_SENSOR = "sensor.test_dehumidifier_humidity"


async def _setup(hass: HomeAssistant, entry=None):
    entry = entry or make_entry()
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_setup_creates_only_verified_read_only_entities(hass: HomeAssistant, cloud: FakeCloud) -> None:
    entry = await _setup(hass)
    assert entry.state is ConfigEntryState.LOADED
    assert cloud.addresses_read == {
        (2, 3),
        (2, 4),
        (2, 5),
        (2, 6),
        (2, 10),
        (3, 2),
        (4, 1),
        (5, 1),
        (7, 1),
        (7, 2),
        (7, 6),
        (7, 7),
    }

    registered = er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)
    assert len(registered) == 12
    assert {entity.entity_id.partition(".")[0] for entity in registered} == {"sensor", "binary_sensor"}
    assert hass.states.get(HUMIDITY_SENSOR).state == "70"
    assert hass.states.get("sensor.test_dehumidifier_target_humidity").state == "55"
    assert hass.states.get("sensor.test_dehumidifier_mode").state == "custom"
    assert hass.states.get("sensor.test_dehumidifier_fan_speed").state == "low"
    assert hass.states.get("binary_sensor.test_dehumidifier_plasma").state == "on"
    assert not cloud.writes


async def test_refresh_updates_the_mode_and_timer(hass: HomeAssistant, cloud: FakeCloud) -> None:
    entry = await _setup(hass)
    cloud.values.update({(2, 3): 1, (7, 1): 1, (7, 2): 1})
    await entry.runtime_data.async_refresh()
    await hass.async_block_till_done()
    assert hass.states.get("sensor.test_dehumidifier_mode").state == "sleep"
    assert hass.states.get("binary_sensor.test_dehumidifier_timer_active").state == "on"
    assert hass.states.get("sensor.test_dehumidifier_timer_duration").state == "1"
    assert not cloud.writes


async def test_location_property_is_never_read(hass: HomeAssistant, cloud: FakeCloud) -> None:
    await _setup(hass)
    # 7/3 holds the place name set in the app.
    assert (7, 3) not in cloud.addresses_read


async def test_private_properties_are_not_polled_or_exported(hass: HomeAssistant, cloud: FakeCloud) -> None:
    entry = await _setup(hass)
    registry = er.async_get(hass)
    assert not any(e.unique_id.endswith(("unknown_6_4", "unknown_7_5")) for e in registry.entities.values())
    assert not ({(1, 5), (6, 4), (7, 3), (7, 5)} & cloud.addresses_read)
    assert await async_get_config_entry_diagnostics(hass, entry) == {
        "profile": {"model": "dreame.dehum.u2512", "status": "mapped"}
    }


async def test_device_info(hass: HomeAssistant, cloud: FakeCloud) -> None:
    from homeassistant.helpers import device_registry as dr

    entry = await _setup(hass)
    # The lookup by entry works on every supported Home Assistant version.
    (device,) = dr.async_entries_for_config_entry(dr.async_get(hass), entry.entry_id)
    assert (DOMAIN, "123456789") in device.identifiers
    assert device.model == "DD20"
    assert device.model_id == "dreame.dehum.u2512"
    assert device.sw_version == "1.0.0_0001"
    assert device.serial_number is None
    assert not device.connections


async def test_unreachable_cloud_retries_setup(hass: HomeAssistant, cloud: FakeCloud) -> None:
    cloud.read_error = CannotConnect("down")
    entry = await _setup(hass)
    assert entry.state is ConfigEntryState.SETUP_RETRY


async def test_short_cloud_outage_keeps_last_values(hass: HomeAssistant, cloud: FakeCloud) -> None:
    entry = await _setup(hass)
    coordinator = entry.runtime_data
    cloud.read_error = CannotConnect("down")
    for _ in range(MAX_FAILED_POLLS):
        await coordinator.async_refresh()
        assert hass.states.get(HUMIDITY_SENSOR).state != STATE_UNAVAILABLE
    await coordinator.async_refresh()
    assert hass.states.get(HUMIDITY_SENSOR).state == STATE_UNAVAILABLE
    cloud.read_error = None
    await coordinator.async_refresh()
    assert hass.states.get(HUMIDITY_SENSOR).state != STATE_UNAVAILABLE


async def test_rejected_account_starts_reauth(hass: HomeAssistant, cloud: FakeCloud) -> None:
    cloud.read_error = AuthFailed("bad")
    entry = await _setup(hass)
    assert entry.state is ConfigEntryState.SETUP_ERROR
    assert any(f["context"]["source"] == "reauth" for f in hass.config_entries.flow.async_progress())


async def test_unsupported_model_raises_issue(hass: HomeAssistant, cloud: FakeCloud) -> None:
    entry = await _setup(hass, make_entry(model="dreame.dehum.unknown"))
    assert entry.state is ConfigEntryState.LOADED
    assert ir.async_get(hass).async_get_issue(DOMAIN, f"unsupported_model_{entry.entry_id}")
    assert not cloud.calls
    assert await hass.config_entries.async_unload(entry.entry_id)


async def test_unload(hass: HomeAssistant, cloud: FakeCloud) -> None:
    entry = await _setup(hass)
    assert await hass.config_entries.async_unload(entry.entry_id)
    assert entry.state is ConfigEntryState.NOT_LOADED
