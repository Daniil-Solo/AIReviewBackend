import asyncio
import logging
import time

from src.constants.ai_pipeline import PipelineStepEnum
from src.constants.ai_review import SolutionStatusEnum
from src.di.container import init_container, shutdown_container
from src.dto.solutions.solutions import SolutionUpdateDTO
from src.infrastructure.logging import get_logger
from src.application.ai_review.preprocessing import prepare_project_tree, prepare_project_content
from src.application.ai_review.project_doc import create_project_doc, generate_critic, resolve_gaps, improve_doc


logger = get_logger()


STEP_HANDLER_MAP = {
    PipelineStepEnum.PREPARE_PROJECT_TREE: prepare_project_tree,
    PipelineStepEnum.PREPARE_PROJECT_CONTENT: prepare_project_content,
    PipelineStepEnum.CREATE_PROJECT_DOC: create_project_doc,
    PipelineStepEnum.GENERATE_CRITIC: generate_critic,
    PipelineStepEnum.RESOLVE_GAPS: resolve_gaps,
    PipelineStepEnum.IMPROVE_DOC: improve_doc,
}


async def run_worker():
    container = await init_container()
    uow = container.uow()
    logger.info("Worker started")
    try:
        while True:
            async with uow.connection():
                task = await uow.pipeline_tasks.get_pending_task()

                if task is None:
                    await asyncio.sleep(2)
                    continue

                logger.info(f"Processing task {task.id}: solution_id={task.solution_id}, step={task.step}")

                marked = await uow.pipeline_tasks.mark_running(task.id)
                if marked is None:
                    continue

            start_time = time.perf_counter()
            try:
                handler = STEP_HANDLER_MAP.get(task.step)
                if not handler:
                    raise ValueError(f"Неизвестный шаг: {task.step}")

                await handler(task.solution_id)
                end_time = time.perf_counter()
                delta = end_time - start_time

                async with uow.connection():
                    solution = await uow.solutions.get_by_id(task.solution_id)
                    if task.step not in solution.steps:
                        await uow.solutions.update(solution.id, SolutionUpdateDTO(steps=[*solution.steps, task.step]))
                    await uow.pipeline_tasks.mark_completed(task.id)
                logger.info(f"Задача успешно выполнена", task_id=task.id, step=task.step)
            except Exception as e:

                logger.exception("Ошибка во время выполнения шага", task_id=task.id, step=task.step)
                async with uow.connection() as conn, conn.transaction():
                    await uow.pipeline_tasks.mark_failed(task.id, str(e))
                    await uow.solutions.update(
                        task.solution_id,
                        SolutionUpdateDTO(status=SolutionStatusEnum.ERROR),
                    )
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
    finally:
        await shutdown_container(container)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_worker())
