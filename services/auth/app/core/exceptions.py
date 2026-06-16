class AppError(Exception):
    def __init__(self, message: str, code: str, status_code: int) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class DuplicateEmailError(AppError):
    def __init__(self) -> None:
        super().__init__("User with this email already exists", "email_already_exists", 409)


class InvalidCredentialsError(AppError):
    def __init__(self) -> None:
        super().__init__("Invalid email or password", "invalid_credentials", 401)


class InvalidTokenError(AppError):
    def __init__(self, code: str = "invalid_token") -> None:
        super().__init__("Invalid or expired token", code, 401)


class UserNotFoundError(AppError):
    def __init__(self) -> None:
        super().__init__("User not found", "user_not_found", 404)
