from src.dto.custom_models.custom_models import (
    CustomModelCreateDTO,
    CustomModelDTO,
    CustomModelRequestCreateDTO,
)
from src.infrastructure.sqlalchemy.uow import UnitOfWork


async def create_custom_model(
    uow: UnitOfWork,
    workspace_id: int,
    user_id: int,
    name: str | None = None,
) -> CustomModelDTO:
    create_data = CustomModelCreateDTO(
        name=name or "test_model",
        model="gpt-4",
        base_url="https://api.example.com",
        encrypted_api_key="gAAAAABp8JhPaj7yfBrCGT2a8mdICOJQH2M-_oE6SQGVQOCuow82WsQmEgY-BrbA3JcoG2WzGiGWnN-xJpcYl-CinFoiO7aKpDOv-EeRpciH6DMfH7eQXl42An8CnB3zw72wmgqUCOhG",
        workspace_id=workspace_id,
    )
    async with uow.connection():
        return await uow.custom_models.create(create_data, user_id)
