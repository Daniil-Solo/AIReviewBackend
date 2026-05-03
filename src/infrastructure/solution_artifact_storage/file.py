from pathlib import Path

from src.infrastructure.solution_artifact_storage.interface import SolutionArtifactStorage


class FileSolutionArtifactStorage(SolutionArtifactStorage):
    def __init__(self, base_path: Path | str) -> None:
        self._base_path = Path(base_path)

    def _get_artifacts_dir(self) -> Path:
        return self._base_path / "artifacts"

    def _make_path(self, solution_id: int, key: str) -> Path:
        return self._get_artifacts_dir() / str(solution_id) / f"{key}.txt"

    async def save_artifact(self, solution_id: int, key: str, content: str) -> None:
        file_path = self._make_path(solution_id, key)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

    async def get_artifact(self, solution_id: int, key: str) -> str:
        file_path = self._make_path(solution_id, key)
        return file_path.read_text(encoding="utf-8")

    async def delete_artifact(self, solution_id: int, key: str) -> None:
        file_path = self._make_path(solution_id, key)
        file_path.unlink(missing_ok=True)
