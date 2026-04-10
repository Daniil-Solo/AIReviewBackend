from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.dto.solutions.solutions import SolutionCreateDTO, SolutionResponseDTO
from src.dto.workspaces.member import WorkspaceMemberCreateDTO
from src.infrastructure.sqlalchemy.uow import UnitOfWork
from tests.factories.solutions import SolutionGitHubFactory
from tests.factories.tasks import TaskFactory
from tests.factories.workspaces import WorkspaceFactory



async def create_github_solution(uow: UnitOfWork, task_id: int, user_id: int) ->  SolutionResponseDTO:
    async with uow.connection():
        data = SolutionGitHubFactory.build(task_id=task_id)
        return await uow.solutions.create(data, user_id)
