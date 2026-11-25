"""Доступ к попыткам прохождения тестов."""

from collections.abc import Mapping

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.models.answer import Answer
from app.models.attempt import Attempt
from app.models.test import Test
from app.repositories.base import BaseRepository
from app.schemas.quiz_check import AnswerEvaluation


class AttemptRepository(BaseRepository):
    """Создание попыток, их чтение и запись оценок открытых ответов."""

    def add(self, attempt: Attempt) -> Attempt:
        """Добавляет попытку с ответами и делает строки видимыми в транзакции."""
        self._session.add(attempt)
        self._session.flush()
        return attempt

    def get_owned(self, user_id: str, attempt_id: str) -> Attempt | None:
        """Попытка по идентификатору, только если она принадлежит пользователю."""
        statement = select(Attempt).where(
            Attempt.id == attempt_id, Attempt.user_id == user_id
        )
        return self._session.scalar(statement)

    def list_for_user(self, user_id: str) -> list[Attempt]:
        """Попытки пользователя, новые сверху, вместе с тестом и материалом.

        Материал нужен в истории: по нему пользователь узнаёт, что именно он
        проходил, не открывая разбор.
        """
        statement = (
            select(Attempt)
            .where(Attempt.user_id == user_id)
            .order_by(Attempt.created_at.desc(), Attempt.id)
            .options(joinedload(Attempt.test).joinedload(Test.material))
        )
        return list(self._session.scalars(statement))

    def apply_open_grades(
        self,
        answers: list[Answer],
        grades: Mapping[str, AnswerEvaluation],
    ) -> None:
        """Пишет балл и комментарий в строки ответов, не завершая транзакцию."""
        for answer in answers:
            grade = grades.get(answer.id)
            if grade is None:
                continue
            answer.llm_score = grade.score
            answer.llm_feedback = grade.feedback
