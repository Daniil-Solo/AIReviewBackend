from src.dto.ai_review.criteria import CriterionCheckDTO, CriterionDTO


async def grade_by_project_doc() -> list[CriterionCheckDTO]:
    criteria = [
        CriterionDTO(
            id=1,
            description="""Покрытие кода тестами должно быть больше 70%"""
        ),
        CriterionDTO(
            id=2,
            description="""Для проекта должен быть написан docker-compose.yaml, которого достаточно для запуска всей системы"""
        ),
        CriterionDTO(
            id=3,
            description="""В проекте присутствует краткий бизнес-план (УТП и описание финансовой модели)"""
        ),
        CriterionDTO(
            id=4,
            description="""Биллинговый блок корректно списывает кредиты (транзакционность операций)"""
        ),
        CriterionDTO(
            id=5,
            description="""Работа модели машинного обучения выполняется в фоне с помощью Celery, arq и подобного"""
        ),
        CriterionDTO(
            id=6,
            description="""
### В проекте настроен мониторинг
В системе присутствуют сервисы для сбора (Prometheus) и визуализации метрик (Grafana)
В коде настроена отправка метрик или эндпоинт для их получения /metrics
"""
        ),
    ]


