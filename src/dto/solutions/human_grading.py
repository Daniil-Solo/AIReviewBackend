from src.dto.common import BaseDTO
from src.dto.criteria import CriterionResponseDTO
from src.dto.solutions.solution_criteria_checks import SolutionCriteriaCheckResponseDTO
from src.dto.solutions.solutions import SolutionResponseDTO
from src.dto.tasks import TaskResponseDTO


class GradingCriterionDTO(BaseDTO):
    criterion: CriterionResponseDTO
    weight: float
    checks: list[SolutionCriteriaCheckResponseDTO]


class CriteriaGradingReviewResponseDTO(BaseDTO):
    solution: SolutionResponseDTO
    task: TaskResponseDTO
    criteria: list[GradingCriterionDTO]
