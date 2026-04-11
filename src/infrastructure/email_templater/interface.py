from abc import ABC, abstractmethod
from typing import Any


class EmailTemplaterInterface(ABC):
    @abstractmethod
    def render(self, **kwargs: Any) -> tuple[str, str, str]:
        """Возвращает тему письма, чистый текст и html"""
        raise NotImplementedError
