import secrets
import string

from src.settings import settings


def generate_code() -> str:
    return "".join(secrets.choice(string.digits) for _ in range(settings.auth.CODE_LENGTH))
