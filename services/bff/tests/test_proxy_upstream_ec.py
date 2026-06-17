from typing import cast
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient, ConnectError, Request

from app.clients.proxy import _upstream_request
from app.core.exceptions import InvalidUpstreamResponseError


@pytest.mark.asyncio
async def test_upstream_request_connection_error_raises_invalid_upstream() -> None:
    """EC-P0 invalid: httpx failure -> 502 invalid_upstream_response."""
    upstream_request = Request("GET", "http://upstream/health")
    mock = AsyncMock()
    mock.request.side_effect = ConnectError("connection failed", request=upstream_request)
    client = cast(AsyncClient, mock)

    try:
        await _upstream_request(client, "GET", "http://upstream/health")
    except InvalidUpstreamResponseError as error:
        assert error.status_code == 502
        assert error.code == "invalid_upstream_response"
    else:
        pytest.fail("Expected InvalidUpstreamResponseError")
