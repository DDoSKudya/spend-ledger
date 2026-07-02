from spend_ledger_common.exceptions import AppError, MissingUserIdError, NotFoundError

__all__ = [
    "AppError",
    "CategoryInUseError",
    "DuplicateNameError",
    "MissingUserIdError",
    "NotFoundError",
    "ValidationError",
]


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
