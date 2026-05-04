import asyncio
from collections.abc import Awaitable, Callable
import datetime
import logging
import time
import traceback

from src.application.ai_review.criteria_grading import grade_by_codebase, grade_by_project_doc
from src.application.ai_review.preprocessing import prepare_project_content, prepare_project_tree
from src.application.ai_review.project_doc import (
    create_project_doc,
    generate_critic,
    improve_doc,
    resolve_gaps,
)
from src.application.ai_review.task_graph import is_step_ready
from src.constants.ai_pipeline import PipelineStepEnum, PipelineTaskStatusEnum
from src.constants.ai_review import SolutionStatusEnum
from src.di.container import init_container, shutdown_container
from src.dto.ai_review.pipeline import PipelineTaskUpdateDTO
from src.dto.solutions.solutions import SolutionUpdateDTO
from src.infrastructure.logging import get_logger


logger = get_logger()


STEP_HANDLER_MAP: dict[PipelineStepEnum, Callable[[int], Awaitable[None]]] = {
    PipelineStepEnum.PREPARE_PROJECT_TREE: prepare_project_tree,
    PipelineStepEnum.PREPARE_PROJECT_CONTENT: prepare_project_content,
    PipelineStepEnum.CREATE_PROJECT_DOC: create_project_doc,
    PipelineStepEnum.GENERATE_CRITIC: generate_critic,
    PipelineStepEnum.RESOLVE_GAPS: resolve_gaps,
    PipelineStepEnum.IMPROVE_DOC: improve_doc,
    PipelineStepEnum.GRADE_BY_PROJECT_DOC: grade_by_project_doc,
    PipelineStepEnum.GRADE_BY_CODEBASE: grade_by_codebase,
}


async def run_worker() -> None:
    container = await init_container()
    uow = container.uow()
    logger.info("Worker started")
    try:
        while True:
            await asyncio.sleep(2)
            async with uow.connection():
                task = await uow.pipeline_tasks.get_ready_pending()
                if task is None:
                    logger.debug("No tasks in queue")
                    continue

            start_time = time.perf_counter()
            try:
                async with uow.connection():
                    solution = await uow.solutions.get_by_id(task.solution_id)
                    if not is_step_ready(task.step, solution.steps):
                        await uow.pipeline_tasks.update_last_checked_at(task.id)
                        logger.debug(f"Task {task.id} not ready, skipping")
                        continue

                    logger.info(f"Processing task {task.id}: solution_id={task.solution_id}, step={task.step}")

                    if solution.status == SolutionStatusEnum.CANCELLED:
                        await uow.pipeline_tasks.update_last_checked_at(task.id)
                        logger.debug(f"Solution {solution.id} is CANCELLED, skipping task {task.id}")
                        continue

                    await uow.pipeline_tasks.update(
                        task.id,
                        PipelineTaskUpdateDTO(
                            status=PipelineTaskStatusEnum.RUNNING, ran_at=datetime.datetime.now(datetime.UTC)
                        ),
                    )

                handler = STEP_HANDLER_MAP.get(task.step)
                if not handler:
                    raise ValueError(f"Неизвестный шаг: {task.step}")

                await handler(task.solution_id)
                success_time = time.perf_counter()

                async with uow.connection():
                    solution = await uow.solutions.get_by_id(task.solution_id)
                    if task.step not in solution.steps:
                        await uow.solutions.update(solution.id, SolutionUpdateDTO(steps=[*solution.steps, task.step]))
                    await uow.pipeline_tasks.update(
                        task.id,
                        PipelineTaskUpdateDTO(
                            status=PipelineTaskStatusEnum.COMPLETED, duration=success_time - start_time
                        ),
                    )
                logger.info("Задача успешно выполнена", task_id=task.id, step=task.step)
            except Exception as e:
                error_time = time.perf_counter()
                logger.exception("Ошибка во время выполнения шага", task_id=task.id, step=task.step)
                try:
                    async with uow.connection() as conn, conn.transaction():
                        await uow.solutions.update(
                            task.solution_id,
                            SolutionUpdateDTO(
                                status=SolutionStatusEnum.ERROR,
                            ),
                        )
                        await uow.pipeline_tasks.update(
                            task.id,
                            PipelineTaskUpdateDTO(
                                status=PipelineTaskStatusEnum.FAILED,
                                error_text=f"{str(e)}\n{traceback.format_exc()}",
                                duration=error_time - start_time,
                            ),
                        )
                except Exception:
                    logger.exception("Ошибка во время сохранения данных об ошибке", task_id=task.id, step=task.step)
                    continue

    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
    finally:
        await shutdown_container(container)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_worker())
