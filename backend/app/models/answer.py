"""Модель ответа пользователя на вопрос попытки."""

from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.base import IdCreatedAtMixin
from app.models.question import Question


class Answer(IdCreatedAtMixin, Base):
    """Ответ на один вопрос попытки.

    Строка создаётся на каждый вопрос теста, даже если пользователь его
    пропустил: тогда `answer_text` и `selected_option_id` оба `NULL`. Так
    уникальность пары «попытка + вопрос» держится без дополнительных проверок,
    а разбор не требует дополнять недостающие строки.
    """

    __tablename__ = "answers"
    __table_args__ = (
        UniqueConstraint("attempt_id", "question_id", name="uq_answers_attempt_question"),
    )

    attempt_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("attempts.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    question_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("questions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    answer_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    selected_option_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("closed_question_options.id", ondelete="SET NULL"),
        nullable=True,
    )
    is_correct_auto: Mapped[bool | None] = mapped_column(nullable=True)
    llm_score: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    llm_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)

    attempt: Mapped["Attempt"] = relationship(back_populates="answers")  # noqa: F821
    question: Mapped[Question] = relationship(Question)
