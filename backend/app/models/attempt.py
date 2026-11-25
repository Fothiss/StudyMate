"""Модель попытки прохождения теста."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.answer import Answer
from app.models.base import IdCreatedAtMixin
from app.models.test import Test

#: Попытка сдана, открытые ответы ещё не проверены.
ATTEMPT_SUBMITTED = "submitted"
#: Открытые ответы проверены моделью.
ATTEMPT_CHECKED = "checked"


class Attempt(IdCreatedAtMixin, Base):
    """Одна сдача сохранённого теста.

    Счёт по тестовым вопросам лежит здесь, потому что он считается при сдаче
    и не меняется. По открытым вопросам баллы хранятся в строках `answers`:
    единая шкала для «верно из N» и «0–100» была бы выдумкой, поэтому
    `final_score` остаётся пустым.
    """

    __tablename__ = "attempts"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    test_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tests.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default=ATTEMPT_SUBMITTED
    )
    choice_correct: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    choice_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    final_score: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    checked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    test: Mapped[Test] = relationship(Test)
    answers: Mapped[list[Answer]] = relationship(
        back_populates="attempt",
        cascade="all, delete-orphan",
    )
