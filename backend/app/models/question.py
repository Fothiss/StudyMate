"""Модели вопросов теста: тестовые с вариантами и открытые с эталоном."""

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.base import IdCreatedAtMixin

#: Тип вопроса с вариантами ответа.
QUESTION_CHOICE = "choice"
#: Тип открытого вопроса с эталонным ответом.
QUESTION_OPEN = "open"


class Question(IdCreatedAtMixin, Base):
    """Вопрос сохранённого теста.

    `order_index` фиксирует порядок вопросов: попытка ссылается на тот же тест,
    поэтому разбор показывает вопросы ровно в том порядке, в котором их видел
    пользователь.
    """

    __tablename__ = "questions"
    __table_args__ = (
        UniqueConstraint("test_id", "order_index", name="uq_questions_test_order"),
    )

    test_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tests.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    type: Mapped[str] = mapped_column(String(16), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    test: Mapped["Test"] = relationship(back_populates="questions")  # noqa: F821
    options: Mapped[list["ClosedQuestionOption"]] = relationship(
        cascade="all, delete-orphan",
        order_by="ClosedQuestionOption.order_index",
    )
    rubric: Mapped["OpenQuestionRubric | None"] = relationship(
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True,
    )


class ClosedQuestionOption(IdCreatedAtMixin, Base):
    """Вариант ответа тестового вопроса.

    Верность хранится на варианте, а не на вопросе: оценка идёт по
    `is_correct`, поэтому подставить правильный ответ из запроса нельзя.
    """

    __tablename__ = "closed_question_options"
    __table_args__ = (
        UniqueConstraint("question_id", "order_index", name="uq_options_question_order"),
    )

    question_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("questions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)


class OpenQuestionRubric(IdCreatedAtMixin, Base):
    """Эталон открытого вопроса: единственный источник истины при проверке."""

    __tablename__ = "open_question_rubrics"

    question_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("questions.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    reference_answer: Mapped[str] = mapped_column(Text, nullable=False)
