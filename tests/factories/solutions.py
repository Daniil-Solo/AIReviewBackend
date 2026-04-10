import factory

from src.constants.ai_review import SolutionFormatEnum
from src.dto.solutions.solutions import SolutionCreateDTO


GITHUB_REPO_LINK = "https://github.com/Daniil-Solo/AIReviewBackend"


class SolutionGitHubFactory(factory.Factory):
    class Meta:
        model = SolutionCreateDTO

    task_id: int
    format = SolutionFormatEnum.GITHUB
    link = GITHUB_REPO_LINK
