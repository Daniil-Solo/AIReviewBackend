from cryptography.fernet import Fernet

from src.infrastructure.encryptor.interface import BaseEncryptor


class FernetEncryptor(BaseEncryptor):
    def __init__(self, encryption_key: str) -> None:
        key = encryption_key.encode()
        self.fernet = Fernet(key)

    def encrypt(self, data: str) -> str:
        encrypted_bytes = self.fernet.encrypt(data.encode())
        return encrypted_bytes.decode()

    def decrypt(self, encrypted_data: str) -> str:
        decrypted_bytes = self.fernet.decrypt(encrypted_data.encode())
        return decrypted_bytes.decode()
