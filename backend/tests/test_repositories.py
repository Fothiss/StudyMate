"""Репозитории тестов и попыток: владение, порядок списка, запись оценок."""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.answer import Answer
from app.models.attempt import Attempt
from app.models.question import QUESTION_OPEN
from app.models.test import Test
from app.models.user import User
from app.repositories.attempts import AttemptRepository
from app.repositories.tests import TestRepository
from app.schemas.quiz_check import AnswerEvaluation
from tests.helpers import make_material, make_user, question_rows, store_test


def test_test_repository_reads_only_owned(session: Session) -> None:
    owner = make_user(session, "owner")
    stranger = make_user(session, "stranger")
    material = make_material(session, owner)
    test = store_test(session, owner, material)
    repository = TestRepository(session)

    assert repository.get_owned(owner.id, test.id) is not None
    assert repository.get_owned(stranger.id, test.id) is None
    assert [stored.id for stored in repository.list_for_material(material.id)] == [test.id]


def test_attempt_repository_starts_empty_and_keeps_owner(session: Session) -> None:
    owner = make_user(session, "owner")
    stranger = make_user(session, "stranger")
    material = make_material(session, owner)
    test = store_test(session, owner, material)
    repository = AttemptRepository(session)

    assert repository.list_for_user(owner.id) == []

    attempt = repository.add(_attempt(session, owner, test))
    session.commit()

    assert repository.get_owned(owner.id, attempt.id) is not None
    assert repository.get_owned(stranger.id, attempt.id) is None
    assert [stored.id for stored in repository.list_for_user(owner.id)] == [attempt.id]
    assert repository.list_for_user(stranger.id) == []


def test_attempt_repository_lists_newest_first(session: Session) -> None:
    owner = make_user(session, "owner")
    material = make_material(session, owner)
    test = store_test(session, owner, material)
    repository = AttemptRepository(session)

    older = repository.add(_attempt(session, owner, test))
    older.created_at = datetime(2024, 1, 1, tzinfo=UTC)
    newer = repository.add(_attempt(session, owner, test))
    newer.created_at = datetime(2024, 1, 2, tzinfo=UTC)
    session.commit()

    assert [stored.id for stored in repository.list_for_user(owner.id)] == [
        newer.id,
        older.id,
    ]


def test_attempt_repository_writes_open_grades(session: Session) -> None:
    owner = make_user(session, "owner")
    material = make_material(session, owner)
    test = store_test(session, owner, material)
    repository = AttemptRepository(session)
    attempt = repository.add(_attempt(session, owner, test))
    session.commit()
    open_answer = next(
        answer for answer in attempt.answers if answer.question.type == QUESTION_OPEN
    )

    repository.apply_open_grades(
        [open_answer],
        {open_answer.id: AnswerEvaluation(score=64, feedback="Частично верно")},
    )
    session.commit()

    stored = session.get(Answer, open_answer.id)
    assert stored is not None
    assert float(stored.llm_score or 0) == 64.0
    assert stored.llm_feedback == "Частично верно"


def _attempt(session: Session, owner: User, test: Test) -> Attempt:
    """Попытка со строкой на каждый вопрос теста."""
    attempt = Attempt(
        user_id=owner.id,
        test_id=test.id,
        choice_correct=0,
        choice_total=1,
    )
    for question in question_rows(session, test.id):
        attempt.answers.append(Answer(question=question))
    return attempt
