from abc import ABC, abstractmethod
from typing import Any


class PromptBuilderInterface(ABC):
    @abstractmethod
    def build(self, **kwargs: Any) -> str:
        raise NotImplementedError