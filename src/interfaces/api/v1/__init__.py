from fastapi import APIRouter

from src.interfaces.api.v1.app.router import router as app_router
from src.interfaces.api.v1.auth.router import router as auth_router
from src.interfaces.api.v1.criteria.router import router as criteria_router
from src.interfaces.api.v1.custom_models import custom_models_router
from src.interfaces.api.v1.joins.router import router as joins_router
from src.interfaces.api.v1.profile.router import router as profile_router
from src.interfaces.api.v1.solutions.router import router as solutions_router
from src.interfaces.api.v1.tasks.router import router as tasks_main_router
from src.interfaces.api.v1.transactions.router import router as transactions_router
from src.interfaces.api.v1.users.router import router as users_router
from src.interfaces.api.v1.workspaces.router import router as workspaces_router


v1_router = APIRouter(prefix="/v1", tags=["v1"])
v1_router.include_router(app_router)
v1_router.include_router(auth_router)
v1_router.include_router(criteria_router)
v1_router.include_router(users_router)
v1_router.include_router(workspaces_router)
v1_router.include_router(joins_router)
v1_router.include_router(tasks_main_router)
v1_router.include_router(solutions_router)
v1_router.include_router(profile_router)
v1_router.include_router(transactions_router)
v1_router.include_router(custom_models_router)

__all__ = ["v1_router"]
