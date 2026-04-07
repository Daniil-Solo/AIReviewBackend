import factory

from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.dto.workspaces.join_rule import WorkspaceJoinRuleRequestCreateDTO
from src.dto.workspaces.member import WorkspaceMemberUpdateDTO
from src.dto.workspaces.workspace import WorkspaceCreateDTO


class WorkspaceFactory(factory.Factory):
    class Meta:
        model = WorkspaceCreateDTO

    name = factory.Faker("name")
    description = factory.Faker("sentence")


class WorkspaceJoinRuleFactory(factory.Factory):
    class Meta:
        model = WorkspaceJoinRuleRequestCreateDTO

    slug = factory.Faker("slug")
    role = WorkspaceMemberRoleEnum.STUDENT
    expired_at = None
    is_active = True
    password = None


class WorkspaceMemberUpdateFactory(factory.Factory):
    class Meta:
        model = WorkspaceMemberUpdateDTO

    role = WorkspaceMemberRoleEnum.STUDENT
