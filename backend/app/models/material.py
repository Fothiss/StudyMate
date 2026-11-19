"""Модель учебного материала."""

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models.base import IdCreatedAtMixin


class Material(IdCreatedAtMixin, Base):
    """Загруженный учебный материал.

    `extracted_text` заполняется при загрузке вместе с `extraction_status`:
    по этому тексту генерируются вопросы, файл повторно не читается.
    """

    __tablename__ = "materials"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    extraction_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
