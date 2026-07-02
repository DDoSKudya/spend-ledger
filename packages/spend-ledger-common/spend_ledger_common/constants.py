ACCESS_TOKEN_TYPE = "access"  # noqa: S105

DEFAULT_HTTP_ERROR_CODES: dict[int, str] = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    409: "conflict",
    422: "validation_error",
    500: "internal_error",
    502: "bad_gateway",
    503: "service_unavailable",
}


def default_http_error_code(status_code: int) -> str:
    return DEFAULT_HTTP_ERROR_CODES.get(status_code, "error")
