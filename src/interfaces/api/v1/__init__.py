from fastapi import APIRouter

from src.interfaces.api.v1.auth.router import router as auth_router
from src.interfaces.api.v1.criteria.router import router as criteria_router
from src.interfaces.api.v1.joins.router import router as joins_router
from src.interfaces.api.v1.users.router import router as users_router
from src.interfaces.api.v1.workspaces.router import router as workspaces_router


v1_router = APIRouter(prefix="/v1", tags=["v1"])
v1_router.include_router(auth_router)
v1_router.include_router(criteria_router)
v1_router.include_router(users_router)
v1_router.include_router(workspaces_router)
v1_router.include_router(joins_router)

__all__ = ["v1_router"]
