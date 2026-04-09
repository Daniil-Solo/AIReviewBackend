from dataclasses import dataclass
import logging
from pathlib import Path
from typing import cast

import tiktoken
from treeproject import path_content, path_tree

from src.application.project.preprocessing.constants import IGNORED_DIRECTORIES, ALLOWED_EXTENSIONS

logger = logging.getLogger(__name__)


def is_ignored_dir(p: Path) -> bool:
    return p.name.startswith(".") or p.name in IGNORED_DIRECTORIES


def include_without_ignored_directories(p: Path) -> bool:
    if p.is_file():
        return True
    return not is_ignored_dir(p)


def include_code_only(p: Path) -> bool:
    if p.is_dir() and not is_ignored_dir(p):
        return True
    return p.is_file() and f".{p.name.split('.')[-1]}" in ALLOWED_EXTENSIONS


@dataclass
class ProjectInfo:
    files_count: int = 0
    chars_count: int = 0
    tokens_count: int = 0


class ProjectPreprocessor:
    def __init__(self, project_path: Path) -> None:
        self._project_path = project_path

    def get_tree(self) -> str:
        return cast("str", path_tree(self._project_path, include=include_without_ignored_directories))

    def get_content(self) -> str:
        return cast("str", path_content(self._project_path, include=include_code_only))

    def _get_files(self) -> list[Path]:
        passed_files = []
        for dirpath, dir_names, file_names in self._project_path.walk(top_down=True):
            dir_names[:] = [d for d in dir_names if include_code_only(dirpath / d)]

            if not include_code_only(dirpath):
                continue

            for file_name in file_names:
                p = dirpath / file_name
                if not include_code_only(p):
                    continue
                passed_files.append(p)
        return passed_files

    def get_info(self) -> ProjectInfo:
        info = ProjectInfo()
        encoding = tiktoken.get_encoding("cl100k_base")

        passed_files = self._get_files()
        info.files_count = len(passed_files)

        for file_path in passed_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                    info.chars_count += len(content)
                    info.tokens_count += len(encoding.encode(content))
            except Exception:
                logger.exception(f"Handling file {file_path}")
                continue

        return info
