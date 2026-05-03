from pathlib import Path
from typing import IO, Any

import uuid

from src.infrastructure.solution_storage.interface import SolutionStorage


class FileSolutionStorage(SolutionStorage):
    def __init__(self, base_path: Path | str | None = None) -> None:
        if base_path is None:
            base_path = Path.cwd() / "file-storage"
        self._base_path = Path(base_path)

    def _get_solutions_dir(self) -> Path:
        return self._base_path / "solutions"

    async def upload_solution(self, file: IO[Any], filename: str, task_id: int, user_id: int) -> str:
        unique_id = uuid.uuid4().hex
        file_dir = self._get_solutions_dir() / str(task_id) / str(user_id)
        file_dir.mkdir(parents=True, exist_ok=True)

        file_key = f"{file_dir}/{unique_id}_{filename}"
        file_path = Path(file_key)
        file_path.write_bytes(file.read())

        return file_key

    async def get_content(self, key: str) -> bytes:
        return Path(key).read_bytes()
