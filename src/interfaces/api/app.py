from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from src.application.exceptions import ApplicationError
from src.infrastructure.di.container import init_container
from src.interfaces.api.error_status_mapping import APP_ERROR_TO_HTTP_CODE
from src.interfaces.api.internal import internal_router
from src.interfaces.api.v1 import v1_router


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    container = init_container()
    yield


def create_app() -> FastAPI:
    application = FastAPI(title="AI Review API", lifespan=lifespan)

    application.include_router(internal_router)
    application.include_router(v1_router)

    @app.exception_handler(ApplicationError)
    async def unicorn_exception_handler(request: Request, exc: ApplicationError):
        return JSONResponse(
            status_code=APP_ERROR_TO_HTTP_CODE[exc.__name__],
            content={"message": exc.message, "code": exc.code},
        )

    return application


app = create_app()
