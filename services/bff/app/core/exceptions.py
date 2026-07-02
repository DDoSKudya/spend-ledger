from spend_ledger_common.exceptions import AppError


class ServiceUnavailableError(AppError):
    def __init__(self, service: str) -> None:
        super().__init__(f"{service} service is not ready", "service_unavailable", 503)


class MissingRefreshTokenError(AppError):
    def __init__(self) -> None:
        super().__init__("Missing refresh token", "missing_refresh_token", 401)


class MissingBearerTokenError(AppError):
    def __init__(self) -> None:
        super().__init__("Missing bearer token", "missing_bearer_token", 401)


class InvalidUpstreamResponseError(AppError):
    def __init__(self, message: str = "Invalid upstream service response") -> None:
        super().__init__(message, "invalid_upstream_response", 502)


class InvalidTokenError(AppError):
    def __init__(self) -> None:
        super().__init__("Invalid token", "invalid_token", 401)
