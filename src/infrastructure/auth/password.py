import hashlib
import secrets


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}.{hashed}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        salt, hashed = hashed_password.split(".")
        computed_hash = hashlib.sha256((plain_password + salt).encode()).hexdigest()
        return secrets.compare_digest(computed_hash, hashed)
    except ValueError:
        return False
