"""Pydantic-схемы учебного материала."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MaterialRead(BaseModel):
    """Карточка материала.

    Внутренний путь к файлу наружу не отдаётся: клиенту достаточно исходного
    имени, а расположение файла — деталь реализации хранилища.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    filename: str
    created_at: datetime
