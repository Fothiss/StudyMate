"""Попытки прохождения тестов: сдача, проверка открытых ответов, чтение."""

from app.models.answer import Answer
from app.models.attempt import ATTEMPT_CHECKED, ATTEMPT_SUBMITTED, Attempt
from app.models.base import utc_now
from app.models.question import (
    QUESTION_CHOICE,
    QUESTION_OPEN,
    ClosedQuestionOption,
    Question,
)
from app.models.user import User
from app.repositories.attempts import AttemptRepository
from app.repositories.tests import TestRepository
from app.schemas.attempt import AttemptAnswerInput
from app.schemas.quiz_check import OpenAnswer
from app.services.ai import AIService
from app.services.open_answers import grade_open_answers


class AttemptService:
    """Сдача сохранённого теста и проверка её открытых ответов.

    Сервис владеет границей транзакции: репозиторий только готовит строки.
    """

    def __init__(
        self,
        attempts: AttemptRepository,
        tests: TestRepository,
        ai: AIService,
    ) -> None:
        self._attempts = attempts
        self._tests = tests
        self._ai = ai

    def submit(
        self,
        user: User,
        test_id: str,
        answers: list[AttemptAnswerInput],
    ) -> Attempt | None:
        """Создаёт попытку и оценивает её тестовые вопросы по данным БД.

        Отвеченным считается только индекс в пределах списка вариантов: такой
        ответ нельзя привязать к чужому вопросу, а индекс вне диапазона
        сохраняется как пропуск.
        """
        test = self._tests.get_owned(user.id, test_id)
        if test is None:
            return None

        given = {answer.question_id: answer for answer in answers}
        attempt = Attempt(
            user_id=user.id,
            test_id=test.id,
            status=ATTEMPT_SUBMITTED,
        )

        choice_total = 0
        choice_correct = 0
        for question in test.questions:
            incoming = given.get(question.id)
            if question.type == QUESTION_CHOICE:
                choice_total += 1
                option = _selected_option(question, incoming)
                is_correct = option.is_correct if option is not None else False
                choice_correct += int(is_correct)
                attempt.answers.append(
                    Answer(
                        question=question,
                        selected_option_id=option.id if option is not None else None,
                        is_correct_auto=is_correct,
                    )
                )
                continue

            text = (incoming.answer_text or "").strip() if incoming is not None else ""
            attempt.answers.append(
                Answer(question=question, answer_text=text or None)
            )

        attempt.choice_total = choice_total
        attempt.choice_correct = choice_correct

        try:
            self._attempts.add(attempt)
            self._attempts.session.commit()
        except BaseException:
            self._attempts.session.rollback()
            raise
        return attempt

    def check(self, user: User, attempt_id: str) -> Attempt | None:
        """Проверяет открытые ответы по эталонам из БД и сохраняет оценки.

        Эталоны берутся из `open_question_rubrics`, поэтому клиент не может
        подставить выгодный ему ответ-эталон. Пока модель не ответила, в базу
        ничего не пишется: ошибка оставляет попытку в прежнем состоянии.
        """
        attempt = self._attempts.get_owned(user.id, attempt_id)
        if attempt is None:
            return None

        open_answers = [
            answer for answer in attempt.answers if answer.question.type == QUESTION_OPEN
        ]
        payload = [
            OpenAnswer(
                question=answer.question.text,
                reference=answer.question.rubric.reference_answer,
                answer=answer.answer_text or "",
            )
            for answer in open_answers
        ]
        # Текст материала обязателен для генерации, поэтому пустая строка здесь
        # возможна только при ручной правке базы.
        grades = grade_open_answers(attempt.test.material.extracted_text or "", payload, self._ai)

        self._attempts.apply_open_grades(
            open_answers,
            {answer.id: grade for answer, grade in zip(open_answers, grades, strict=True)},
        )
        attempt.status = ATTEMPT_CHECKED
        attempt.checked_at = utc_now()

        try:
            self._attempts.session.commit()
        except BaseException:
            self._attempts.session.rollback()
            raise
        return attempt

    def list(self, user: User) -> list[Attempt]:
        """Попытки пользователя, новые сверху."""
        return self._attempts.list_for_user(user.id)

    def get(self, user: User, attempt_id: str) -> Attempt | None:
        """Попытка пользователя; чужая неотличима от отсутствующей."""
        return self._attempts.get_owned(user.id, attempt_id)


def _selected_option(
    question: Question,
    incoming: AttemptAnswerInput | None,
) -> ClosedQuestionOption | None:
    """Вариант по присланной позиции: индекс вне диапазона — пропуск."""
    if incoming is None or incoming.selected_index is None:
        return None
    if incoming.selected_index >= len(question.options):
        return None
    return question.options[incoming.selected_index]
