from fastapi import FastAPI

from src.interfaces.api.internal import internal_router


def create_app() -> FastAPI:
    app = FastAPI(title="AutoReviewer API")
    app.include_router(internal_router)
    return app


app = create_app()
