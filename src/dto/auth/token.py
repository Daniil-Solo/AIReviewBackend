from src.dto.common import BaseDTO


class UserLoginDTO(BaseDTO):
    email: str
    password: str


class TokenDTO(BaseDTO):
    access_token: str
