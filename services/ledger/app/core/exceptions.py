class AppError(Exception):
    def __init__(self, message: str, code: str, status_code: int) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class UnauthorizedError(AppError):
    def __init__(
        self, message: str = "Missing X-User-Id header", code: str = "missing_user_id"
    ) -> None:
        super().__init__(message, code, 401)


class NotFoundError(AppError):
    def __init__(self, resource: str) -> None:
        super().__init__(f"{resource} not found", f"{resource}_not_found", 404)


class CategoryInUseError(AppError):
    def __init__(self, count: int) -> None:
        super().__init__(
            f"Category is used by {count} expenses",
            "category_in_use",
            409,
        )


class DuplicateNameError(AppError):
    def __init__(self, resource: str) -> None:
        super().__init__(
            f"{resource} with this name already exists",
            f"{resource}_duplicate_name",
            409,
        )


class ValidationError(AppError):
    def __init__(self, message: str, code: str = "validation_error") -> None:
        super().__init__(message, code, 422)
