import csv
import io
import logging

import sqlalchemy as sa
from dependency_injector.wiring import Provide, inject

from src.application.workspaces.common import check_member_role
from src.constants.workspaces import WorkspaceMemberRoleEnum
from src.di.container import Container
from src.dto.tasks import TaskFiltersDTO
from src.dto.workspaces.member import WorkspaceMemberFiltersDTO
from src.dto.workspaces.student_grades import StudentGradesDTO, StudentGradesFiltersDTO, TaskGradeDTO
from src.infrastructure.sqlalchemy.models import solutions_table, tasks_table, users_table, workspace_members_table
from src.infrastructure.sqlalchemy.uow import UnitOfWork


@inject
async def get_student_grades(
    workspace_id: int,
    filters: StudentGradesFiltersDTO,
    user_id: int,
    uow: UnitOfWork = Provide[Container.uow],
) -> list[StudentGradesDTO]:
    async with uow.connection():
        await check_member_role(
            uow, user_id, workspace_id, {WorkspaceMemberRoleEnum.TEACHER, WorkspaceMemberRoleEnum.OWNER}
        )
        tasks = await uow.tasks.get_list(TaskFiltersDTO(workspace_id=workspace_id, ids=filters.task_ids))
        if not tasks:
            return []
        task_ids = [task.id for task in tasks]

        members = await uow.workspace_members.get_list(WorkspaceMemberFiltersDTO(workspace_id=workspace_id))
        user_ids = filters.user_ids or [member.user_id for member in members]

        students = await uow.users.get_by_ids(user_ids)
        if not students:
            return []

        best_grades = await uow.solutions.get_best_grades(task_ids, user_ids)

        return [
                StudentGradesDTO(
                    user=student.as_short(),
                    tasks=[
                        TaskGradeDTO(
                            task_id=task.id,
                            task_name=task.name,
                            grade=best_grades.get((student.id, task.id))[0] if (student.id, task.id) in best_grades else None,
                            best_solution_id=best_grades.get((student.id, task.id))[1] if (student.id, task.id) in best_grades else None,
                        )
                        for task in tasks
                    ],
                )
                for student in students
            ]


@inject
async def get_student_grades_csv(
    workspace_id: int,
    filters: StudentGradesFiltersDTO,
    user_id: int,
    uow: UnitOfWork = Provide[Container.uow],
) -> str:
    student_grades = await get_student_grades(workspace_id, filters, user_id, uow=uow)

    if not student_grades:
        return "fullname\n"

    headers = ["fullname"] + [task.task_name for task in student_grades[0].tasks]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)

    for sg in student_grades:
        row = [sg.user.fullname]
        for task in sg.tasks:
            row.append(str(task.grade) if task.grade is not None else "")
        writer.writerow(row)

    return output.getvalue()
