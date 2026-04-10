from dependency_injector.wiring import Provide, inject
from pydantic import TypeAdapter

from src.di.container import Container
from src.dto.ai_review.criteria import CriterionCheckDTO, CriterionWithCommentsDTO
from src.dto.ai_review.message import InputMessageDTO
from src.infrastructure.ai.llm.interface import LLMInterface
from src.infrastructure.ai.prompt_builder.interface import PromptBuilderInterface
from src.infrastructure.logging import get_logger
from src.infrastructure.sqlalchemy.uow import UnitOfWork
from src.settings import ROOT_DIR


logger = get_logger()


@inject
async def grade_by_project_doc(
    uow: UnitOfWork = Provide[Container.uow],
    prompt_builder: PromptBuilderInterface = Provide[Container.prompt_builder],
    default_model: LLMInterface = Provide[Container.default_model],
) -> None:  # list[CriterionCheckDTO]
    criteria = [
        CriterionWithCommentsDTO(id=534, description="""Покрытие кода тестами должно быть больше 70%"""),
        CriterionWithCommentsDTO(
            id=66,
            description="""Для проекта должен быть написан docker-compose.yaml, которого достаточно для запуска всей системы""",
        ),
        CriterionWithCommentsDTO(
            id=21, description="""В проекте присутствует краткий бизнес-план (УТП и описание финансовой модели)"""
        ),
        CriterionWithCommentsDTO(
            id=22, description="""Биллинговый блок корректно списывает кредиты (транзакционность операций)"""
        ),
        CriterionWithCommentsDTO(
            id=23,
            description="""Работа модели машинного обучения выполняется в фоне с помощью Celery, arq и подобного""",
        ),
        CriterionWithCommentsDTO(
            id=85,
            description="""
### В проекте настроен мониторинг
В системе присутствуют сервисы для сбора (Prometheus) и визуализации метрик (Grafana)
В коде настроена отправка метрик или эндпоинт для их получения /metrics
""",
        ),
    ]
    with open(ROOT_DIR / "examples" / "project_docs" / "avito-price-prediction" / "final_project_doc.md") as f:
        project_doc = f.read()

    system_content = prompt_builder.build(
        prompt_path="criteria_checks/projectdoc_grading/system.tpl", criteria=criteria
    )
    user_content = prompt_builder.build(
        prompt_path="criteria_checks/projectdoc_grading/user.tpl", project_doc=project_doc
    )

    messages = [
        InputMessageDTO(role="system", content=system_content),
        InputMessageDTO(role="user", content=user_content),
    ]

    answer = default_model.answer(messages)
    with open("grade_by_project_doc.txt", "w") as f:
        f.write(answer.content)

    if answer.content is not None:
        criteria_checks = TypeAdapter(list[CriterionCheckDTO]).validate_json(answer.content)
        logger.info("criteria_checks", criteria_checks=criteria_checks)


@inject
async def grade_by_codebase(
    prompt_builder: PromptBuilderInterface = Provide[Container.prompt_builder],
    default_model: LLMInterface = Provide[Container.default_model],
) -> None:  # list[CriterionCheckDTO]
    criteria = [
        CriterionWithCommentsDTO(
            id=66,
            description="""Для проекта должен быть написан docker-compose.yaml, которого достаточно для запуска всей системы""",
            comments=[
                "В структуре проекта и описании зависимостей отсутствует упоминание файла docker-compose.yaml. Также не указано, что проект упакован в Docker-контейнеры или может быть запущен через Docker. Архитектура предполагает запуск скриптов локально (main.py), без контейнеризации. Вероятно, файл docker-compose.yaml отсутствует. Для проверки требуется анализ корневой директории проекта.",
            ],
        ),
    ]
    with open(ROOT_DIR / "examples" / "project_docs" / "avito-price-prediction" / "project_content.md") as f:
        project_content_doc = f.read()

    with open(ROOT_DIR / "examples" / "project_docs" / "avito-price-prediction" / "project_tree.md") as f:
        project_tree_doc = f.read()

    system_content = prompt_builder.build(prompt_path="criteria_checks/codebase_grading/system.tpl", criteria=criteria)
    user_content = prompt_builder.build(
        prompt_path="criteria_checks/codebase_grading/user.tpl",
        project_tree=project_tree_doc,
        project_content=project_content_doc,
    )

    messages = [
        InputMessageDTO(role="system", content=system_content),
        InputMessageDTO(role="user", content=user_content),
    ]

    answer = default_model.answer(messages)
    with open("grade_by_codebase.txt", "w") as f:
        f.write(answer.content)

    if answer.content is not None:
        criteria_checks = TypeAdapter(list[CriterionCheckDTO]).validate_json(answer.content)
        logger.info("criteria_checks", criteria_checks=criteria_checks)
