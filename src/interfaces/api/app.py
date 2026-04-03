from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.application.exceptions import ApplicationError
from src.di.container import init_container
from src.interfaces.api.error_status_mapping import APP_ERROR_TO_HTTP_CODE
from src.interfaces.api.internal import internal_router
from src.interfaces.api.v1 import v1_router


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    container = init_container()
    yield
    engine = container.engine()
    await engine.dispose()


def create_app() -> FastAPI:
    application = FastAPI(title="AI Review API", lifespan=lifespan)

    application.include_router(internal_router, prefix="/api")
    application.include_router(v1_router, prefix="/api")

    @application.exception_handler(ApplicationError)
    async def application_error_handler(_request: Request, exc: ApplicationError) -> JSONResponse:
        return JSONResponse(
            status_code=APP_ERROR_TO_HTTP_CODE.get(exc.__class__.__name__, 500),
            content={"message": exc.message, "code": exc.code},
        )

    return application


app = create_app()
