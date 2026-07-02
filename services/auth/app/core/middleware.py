from fastapi import Request

from spend_ledger_common.middleware import DEFAULT_STATELESS_PATHS


def auth_needs_db_session(request: Request) -> bool:
    if request.url.path in DEFAULT_STATELESS_PATHS:
        return False
    if request.url.path == "/internal/v1/auth/verify":
        authorization = request.headers.get("Authorization", "")
        return authorization.startswith("Bearer ")
    return True
