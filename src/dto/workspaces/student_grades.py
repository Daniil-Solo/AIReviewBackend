from pydantic import Field

from src.dto.common import BaseDTO
from src.dto.users.user import ShortUserDTO


class StudentGradesFiltersDTO(BaseDTO):
    task_ids: list[int] | None = Field(default=None, description="Фильтр по ID задач")
    user_ids: list[int] | None = Field(default=None, description="Фильтр по ID студентов")


class TaskGradeDTO(BaseDTO):
    task_id: int = Field(description="ID задачи")
    task_name: str = Field(description="Название задачи")
    best_solution_id: int | None = Field(description="Идентификатор лучшего решения")
    grade: int | None = Field(description="Оценка (None если нет оценки)")


class StudentGradesDTO(BaseDTO):
    user: ShortUserDTO = Field(description="Пользователь")
    tasks: list[TaskGradeDTO] = Field(description="Список задач с оценками")
