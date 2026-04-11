from fastapi import status

from src.application.exceptions import (
    ApplicationError,
    ConflictError,
    EntityNotFoundError,
    ForbiddenError,
    InvalidCredentialsError,
    RateLimitError,
)


APP_ERROR_TO_HTTP_CODE = {
    ApplicationError.__name__: status.HTTP_400_BAD_REQUEST,
    EntityNotFoundError.__name__: status.HTTP_404_NOT_FOUND,
    InvalidCredentialsError.__name__: status.HTTP_401_UNAUTHORIZED,
    ConflictError.__name__: status.HTTP_409_CONFLICT,
    ForbiddenError.__name__: status.HTTP_403_FORBIDDEN,
    RateLimitError.__name__: status.HTTP_429_TOO_MANY_REQUESTS,
}
