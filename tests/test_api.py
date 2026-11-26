"""The cloud client's handling of replies."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.dreame_dehum.api import CannotConnect, CommandFailed, DreameCloud


async def test_missing_addresses_are_dropped() -> None:
    cloud = DreameCloud(None, "user@example.com", "x", "eu")  # type: ignore[arg-type]
    reply: list[dict[str, Any]] = [
        {"siid": 2, "piid": 1, "code": 0, "value": 1},
        {"siid": 2, "piid": 8, "code": 0, "value": -4001},  # no such property
        {"siid": 8, "piid": 1, "code": 0, "value": -4005},  # no such service
        {"siid": 3, "piid": 2, "code": 0, "value": None},
        {"siid": 3, "piid": 3, "code": -1, "value": 20},
    ]
    cloud._command = AsyncMock(return_value=reply)  # type: ignore[method-assign]
    values = await cloud.get_properties("1", None, [(2, 1), (2, 8), (8, 1), (3, 2), (3, 3)])
    assert values == {(2, 1): 1}


@pytest.mark.parametrize("operation", ["login", "get_devices"])
async def test_http_redirects_are_not_followed(operation: str) -> None:
    session = MagicMock()
    session.post.return_value.__aenter__.return_value = MagicMock(status=307)
    cloud = DreameCloud(session, "user@example.com", "synthetic-password", "eu")
    cloud._access_token = "synthetic-token"
    cloud._expires_at = float("inf")

    with pytest.raises(CannotConnect, match="HTTP 307"):
        await getattr(cloud, operation)()

    assert session.post.call_count == 1
    assert session.post.call_args.kwargs["allow_redirects"] is False


async def test_rpc_rejects_unexpected_routing_before_transport() -> None:
    cloud = DreameCloud(MagicMock(), "user@example.com", "synthetic-password", "eu")
    transport = AsyncMock()
    cloud._post_json = transport  # type: ignore[method-assign]

    with pytest.raises(CannotConnect, match="Unexpected Dreame routing information"):
        await cloud.get_properties("4242", "10000.mt.us.iot.dreame.tech:19973", [(3, 2)])

    transport.assert_not_awaited()


async def test_lab_rejects_writes_before_transport() -> None:
    cloud = DreameCloud(MagicMock(), "user@example.com", "synthetic-password", "eu")
    transport = AsyncMock()
    cloud._post_json = transport  # type: ignore[method-assign]
    with pytest.raises(CommandFailed, match="read-only"):
        await cloud.set_property("4242", "10000.mt.eu.iot.dreame.tech:19973", 7, 7, 1)
    with pytest.raises(CommandFailed, match="read-only"):
        await cloud.call_action("4242", "10000.mt.eu.iot.dreame.tech:19973", 2, 1)
    transport.assert_not_awaited()
