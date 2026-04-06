class ApplicationError(Exception):
    def __init__(self, message: str, code: str) -> None:
        self.message = message
        self.code = code
        super().__init__(self.message)


class EntityNotFoundError(ApplicationError):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message, "not_found")


class InvalidCredentialsError(ApplicationError):
    pass


class ConflictError(ApplicationError):
    pass


class ForbiddenError(ApplicationError):
    def __init__(self, message: str, code: str = "forbidden") -> None:
        self.message = message
        self.code = code
        super().__init__(self.message, self.code)
