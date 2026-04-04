from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import ExpiredSignatureError

from src.application.exceptions import InvalidCredentialsError
from src.dto.users.user import ShortUserDTO
from src.infrastructure.auth.jwt import decode_token


bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),  # noqa: B008
) -> ShortUserDTO:
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except ExpiredSignatureError:
        raise InvalidCredentialsError(message="Токен устарел", code="token_expired")
    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise InvalidCredentialsError(message="Токен невалидный", code="token_invalid")
    return ShortUserDTO(**payload)
