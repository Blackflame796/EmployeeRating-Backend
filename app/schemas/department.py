# Схемы Pydantic для отделов
from pydantic import BaseModel, ConfigDict

class DepartmentSchema(BaseModel):
    """Базовая схема для создания/обновления отдела"""
    model_config = ConfigDict(from_attributes=True)
    name: str # Название отдела (уникальное)

class DepartmentResponse(DepartmentSchema):
    """Схема ответа для отдела (включает ID)"""
    id: int
