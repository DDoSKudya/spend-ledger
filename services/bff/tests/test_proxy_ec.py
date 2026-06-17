import json

import pytest

from app.clients.proxy import _normalize_error_body


@pytest.mark.parametrize(
    ("status_code", "content", "content_type", "expected"),
    [
        (
            200,
            b'{"ok": true}',
            "application/json",
            b'{"ok": true}',
        ),
        (
            404,
            b'{"detail": "not found", "code": "not_found"}',
            "application/json",
            b'{"detail": "not found", "code": "not_found"}',
        ),
        (
            404,
            b'{"detail": "Category not found"}',
            "application/json",
            json.dumps({"detail": "Category not found", "code": "not_found"}).encode(),
        ),
        (
            502,
            b"bad gateway",
            "text/plain",
            json.dumps({"detail": "Upstream error", "code": "bad_gateway"}).encode(),
        ),
    ],
)
def test_normalize_error_body(status_code, content, content_type, expected) -> None:
    assert _normalize_error_body(status_code, content, content_type) == expected
