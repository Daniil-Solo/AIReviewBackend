from dependency_injector.wiring import inject, Provide
from pydantic import TypeAdapter

from src.di.container import Container
from src.dto.ai_review.criteria import CriterionDTO, CriterionCheckDTO
from src.dto.ai_review.message import InputMessageDTO
from src.infrastructure.ai.prompt_builder.interface import PromptBuilderInterface
from src.infrastructure.ai.llm.interface import LLMInterface
from src.infrastructure.logging import get_logger
from src.settings import ROOT_DIR


logger = get_logger()

@inject
async def grade_by_project_doc(
    prompt_builder: PromptBuilderInterface = Provide[Container.prompt_builder],
    default_model: LLMInterface = Provide[Container.default_model]
) -> None: # list[CriterionCheckDTO]
    criteria = [
        CriterionDTO(
            id=534,
            description="""Покрытие кода тестами должно быть больше 70%"""
        ),
        CriterionDTO(
            id=66,
            description="""Для проекта должен быть написан docker-compose.yaml, которого достаточно для запуска всей системы"""
        ),
        CriterionDTO(
            id=21,
            description="""В проекте присутствует краткий бизнес-план (УТП и описание финансовой модели)"""
        ),
        CriterionDTO(
            id=22,
            description="""Биллинговый блок корректно списывает кредиты (транзакционность операций)"""
        ),
        CriterionDTO(
            id=23,
            description="""Работа модели машинного обучения выполняется в фоне с помощью Celery, arq и подобного"""
        ),
        CriterionDTO(
            id=85,
            description="""
### В проекте настроен мониторинг
В системе присутствуют сервисы для сбора (Prometheus) и визуализации метрик (Grafana)
В коде настроена отправка метрик или эндпоинт для их получения /metrics
"""
        ),
    ]
    with open(ROOT_DIR / "examples" / "project_docs" / "aith-courses" / "final_project_doc.md", "r") as f:
        project_doc = f.read()

    system_content = prompt_builder.build(
        prompt_path="criteria_checks/projectdoc_grading/system.tpl",
        criteria=criteria
    )
    user_content = prompt_builder.build(
        prompt_path="criteria_checks/projectdoc_grading/user.tpl",
        project_doc=project_doc
    )

    messages = [
        InputMessageDTO(role="system", content=system_content),
        InputMessageDTO(role="user", content=user_content),
    ]

    answer = default_model.answer(messages)
    with open("result.txt", "w") as f:
        f.write(answer.content)

    if answer.content is not None:
        criteria_checks = TypeAdapter([CriterionCheckDTO]).validate_json(answer.content)
        logger.info("criteria_checks", criteria_checks=criteria_checks)
