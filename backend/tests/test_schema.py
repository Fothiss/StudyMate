"""Схема БД: новые таблицы, уникальность ответа и каскадные удаления."""

import pytest
from sqlalchemy import Engine, inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.answer import Answer
from app.models.attempt import Attempt
from app.models.question import ClosedQuestionOption, OpenQuestionRubric, Question
from app.models.test import Test
from tests.helpers import make_material, make_user, question_rows, store_test

EXPECTED_TABLES = {
    "answers",
    "attempts",
    "closed_question_options",
    "materials",
    "open_question_rubrics",
    "questions",
    "tests",
    "users",
}


def test_create_all_adds_new_tables(engine: Engine) -> None:
    assert EXPECTED_TABLES <= set(inspect(engine).get_table_names())


def test_unanswered_answer_is_stored_once(session: Session) -> None:
    user = make_user(session, "owner")
    material = make_material(session, user)
    test = store_test(session, user, material)
    question = question_rows(session, test.id)[0]

    attempt = Attempt(
        user_id=user.id,
        test_id=test.id,
        choice_correct=0,
        choice_total=1,
    )
    attempt.answers.append(Answer(question_id=question.id))
    session.add(attempt)
    session.commit()

    stored = session.scalars(select(Answer)).one()
    assert stored.answer_text is None
    assert stored.selected_option_id is None

    session.add(Answer(attempt_id=attempt.id, question_id=question.id))
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_deleting_test_removes_related_rows(session: Session) -> None:
    user = make_user(session, "owner")
    material = make_material(session, user)
    test = store_test(session, user, material)
    questions = question_rows(session, test.id)
    attempt = Attempt(user_id=user.id, test_id=test.id)
    for question in questions:
        attempt.answers.append(Answer(question_id=question.id))
    session.add(attempt)
    session.commit()

    session.delete(test)
    session.commit()

    for model in (Question, ClosedQuestionOption, OpenQuestionRubric, Attempt, Answer):
        assert session.scalars(select(model)).all() == []


def test_deleting_material_removes_tests(session: Session) -> None:
    user = make_user(session, "owner")
    material = make_material(session, user)
    store_test(session, user, material)
    session.commit()

    session.delete(material)
    session.commit()

    assert session.scalars(select(Test)).all() == []
    assert session.scalars(select(Question)).all() == []
