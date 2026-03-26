from abc import abstractmethod
from typing import Generic, TypeVar

from tree_sitter import Language, Parser
import tree_sitter_python as tsp


PY_LANGUAGE = Language(tsp.language())

T = TypeVar("T")


class BaseASTAnalyzer(Generic[T]):
    def __init__(self) -> None:
        self._language = PY_LANGUAGE
        self._parser = Parser(self._language)

    @abstractmethod
    def analyze(self, source: bytes) -> T:
        raise NotImplementedError
