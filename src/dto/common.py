from pydantic import BaseModel, Field


class BaseDTO(BaseModel):
    class Config:
        from_attributes = True


class SuccessOperationDTO(BaseDTO):
    message: str = Field(description="Сообщение об успешно выполненной операции")
