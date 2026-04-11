import datetime
from typing import Any

import jwt

from src.dto.users.user import ShortUserDTO
from src.settings import settings


def create_access_token(user: ShortUserDTO) -> str:
    expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    data = dict(exp=expire, sub=str(user.id), **user.model_dump(by_alias=True))
    return jwt.encode(data, settings.auth.SECRET_KEY, algorithm=settings.auth.ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.auth.SECRET_KEY, algorithms=[settings.auth.ALGORITHM])
