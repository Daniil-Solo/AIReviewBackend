from pydantic import Field

from src.dto.common import BaseDTO


class StudentGradesFiltersDTO(BaseDTO):
    task_ids: list[int] | None = Field(default=None, description="Фильтр по ID задач")
    user_ids: list[int] | None = Field(default=None, description="Фильтр по ID студентов")


class TaskGradeDTO(BaseDTO):
    task_id: int = Field(description="ID задачи")
    task_name: str = Field(description="Название задачи")
    grade: int | None = Field(default=None, description="Оценка (None если нет оценки)")


class StudentGradesDTO(BaseDTO):
    user_id: int = Field(description="ID студента")
    user_fullname: str = Field(description="Полное имя студента")
    user_email: str = Field(description="Email студента")
    tasks: list[TaskGradeDTO] = Field(description="Список задач с оценками")
