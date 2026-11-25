"""Модель сохранённого теста."""

from typing import Any

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.base import IdCreatedAtMixin
from app.models.material import Material
from app.models.question import Question


class Test(IdCreatedAtMixin, Base):
    """Сгенерированный тест по материалу.

    Каждая генерация создаёт новую строку: попытка ссылается на неизменный
    тест, иначе разбор старой попытки показывал бы другие вопросы.
    """

    __tablename__ = "tests"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    material_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("materials.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    summary: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    generation_params: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    material: Mapped[Material] = relationship(Material)
    questions: Mapped[list[Question]] = relationship(
        back_populates="test",
        cascade="all, delete-orphan",
        order_by="Question.order_index",
    )
