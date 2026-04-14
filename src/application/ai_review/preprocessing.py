import io
import tempfile
import zipfile
from pathlib import Path

import httpx
from dependency_injector.wiring import Provide, inject

from src.application.ai_review.task_graph import PipelineStepEnum
from src.constants.ai_review import SolutionFormatEnum
from src.constants.preprocessing import IGNORED_DIRECTORIES, ALLOWED_EXTENSIONS
from src.di.container import Container
from src.infrastructure.logging import get_logger
from src.infrastructure.storage.artifact import SolutionArtifactStorage
from src.infrastructure.sqlalchemy.uow import UnitOfWork
from src.infrastructure.storage.interface import SolutionStorage
from treeproject import path_content, path_tree

logger = get_logger()


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


@inject
async def _get_project_bytes(
        solution_format: SolutionFormatEnum,
        solution_link: str,
        solution_storage: SolutionStorage = Provide[Container.solution_storage],
) -> bytes:
    if solution_format == SolutionFormatEnum.GITHUB:
        async with httpx.AsyncClient() as client:
            for branch in ["main", "master", "dev"]:
                response = await client.get(f"{solution_link}/archive/refs/heads/{branch}.zip")
                if response.status_code == 200:
                    return response.content
            raise ValueError(f"Не удалось запросить данные из репозитория {solution_link}")
    else:
        return await solution_storage.get_content(solution_link)


@inject
async def prepare_project_tree(
        solution_id: int,
        artifact_storage: SolutionArtifactStorage = Provide[Container.solution_artifact_storage],
        uow: UnitOfWork = Provide[Container.uow],
) -> None:
    async with uow.connection():
        solution = await uow.solutions.get_by_id(solution_id)

    project_bytes = await _get_project_bytes(solution.format, solution.link)

    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(io.BytesIO(project_bytes)) as zf:
            zf.extractall(temp_dir)

        project_tree = path_tree(Path(temp_dir), include=include_without_ignored_directories)

    await artifact_storage.save_artifact(solution_id, PipelineStepEnum.PREPARE_PROJECT_TREE, project_tree)


@inject
async def prepare_project_content(
        solution_id: int,
        artifact_storage: SolutionArtifactStorage = Provide[Container.solution_artifact_storage],
        uow: UnitOfWork = Provide[Container.uow],
) -> None:
    async with uow.connection():
        solution = await uow.solutions.get_by_id(solution_id)

    project_bytes = await _get_project_bytes(solution.format, solution.link)

    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(io.BytesIO(project_bytes)) as zf:
            zf.extractall(temp_dir)

        project_tree = path_content(Path(temp_dir), include=include_code_only)

    await artifact_storage.save_artifact(solution_id, PipelineStepEnum.PREPARE_PROJECT_CONTENT, project_tree)
