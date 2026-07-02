from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from spend_ledger_common.constants import default_http_error_code
from spend_ledger_common.exceptions import AppError


def error_response_for(exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "code": exc.code},
    )


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return error_response_for(exc)

    @app.exception_handler(HTTPException)
    async def handle_http_exception(_: Request, exc: HTTPException) -> JSONResponse:
        detail = exc.detail
        if isinstance(detail, dict):
            message = str(detail.get("detail", detail))
            code = str(detail.get("code", default_http_error_code(exc.status_code)))
        else:
            message = str(detail)
            code = default_http_error_code(exc.status_code)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": message, "code": code},
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Validation failed",
                "code": "validation_error",
                "errors": exc.errors(),
            },
        )
