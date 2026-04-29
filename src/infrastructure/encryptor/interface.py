from abc import ABC, abstractmethod


class BaseEncryptor(ABC):
    @abstractmethod
    def encrypt(self, data: str) -> str:
        pass

    @abstractmethod
    def decrypt(self, encrypted_data: str) -> str:
        pass
