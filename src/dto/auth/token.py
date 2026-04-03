from pydantic import BaseModel


class UserLoginDTO(BaseModel):
    email: str
    password: str


class TokenDTO(BaseModel):
    access_token: str
