"""Сдача теста, проверка открытых ответов, история и разбор попытки."""

import time
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.answer import Answer
from app.models.attempt import ATTEMPT_CHECKED, ATTEMPT_SUBMITTED, Attempt
from app.models.question import QUESTION_CHOICE, QUESTION_OPEN, Question
from app.schemas.quiz import OpenQuestion, Quiz
from app.schemas.quiz_check import AnswerEvaluation
from app.services.gigachat import QuizGenerationError
from tests.helpers import FakeAI, generate_test, option_rows, question_rows

OPEN_TEXT = "Фотосинтез превращает свет в химическую энергию"


def _questions(session: Session, test_id: str) -> dict[str, Question]:
    """Вопросы теста по типу."""
    rows = question_rows(session, test_id)
    return {question.type: question for question in rows}


def _option(session: Session, question: Question, *, correct: bool) -> str:
    """Идентификатор верного или неверного варианта."""
    return next(
        option.id for option in option_rows(session, question.id) if option.is_correct is correct
    )


def _submit(
    api: TestClient,
    headers: dict[str, str],
    test_id: str,
    answers: list[dict[str, Any]],
) -> Any:
    """Сдаёт тест через API, не проверяя код ответа."""
    return api.post(
        f"/tests/{test_id}/attempts", json={"answers": answers}, headers=headers
    )


def _open_quiz(count: int = 1) -> Quiz:
    """Тест только из открытых вопросов."""
    return Quiz(
        summary=["Краткое содержание"],
        questions=[
            OpenQuestion(
                kind="open",
                text=f"Открытый вопрос {number}",
                reference=f"Эталон {number}",
            )
            for number in range(count)
        ],
    )


def test_choice_answer_is_graded_on_server(
    api: TestClient,
    auth: dict[str, str],
    material: dict[str, object],
    session: Session,
) -> None:
    test_id = generate_test(api, auth, str(material["id"]))["test_id"]
    choice = _questions(session, test_id)[QUESTION_CHOICE]

    response = _submit(
        api,
        auth,
        test_id,
        [{"question_id": choice.id, "selected_option_id": _option(session, choice, correct=True)}],
    )

    assert response.status_code == 201
    body = response.json()
    assert body["attempt_id"]
    assert body["status"] == ATTEMPT_SUBMITTED
    assert body["choice_correct"] == 1
    assert body["choice_total"] == 1

    answers = session.scalars(select(Answer)).all()
    assert len(answers) == 2
    stored = next(answer for answer in answers if answer.question_id == choice.id)
    assert stored.is_correct_auto is True


def test_wrong_option_is_incorrect(
    api: TestClient,
    auth: dict[str, str],
    material: dict[str, object],
    session: Session,
) -> None:
    test_id = generate_test(api, auth, str(material["id"]))["test_id"]
    choice = _questions(session, test_id)[QUESTION_CHOICE]

    response = _submit(
        api,
        auth,
        test_id,
        [{"question_id": choice.id, "selected_option_id": _option(session, choice, correct=False)}],
    )

    assert response.status_code == 201
    assert response.json()["choice_correct"] == 0


def test_unanswered_question_is_stored_and_counted(
    api: TestClient,
    auth: dict[str, str],
    material: dict[str, object],
    session: Session,
) -> None:
    test_id = generate_test(api, auth, str(material["id"]))["test_id"]

    response = _submit(api, auth, test_id, [])

    assert response.status_code == 201
    body = response.json()
    assert body["choice_correct"] == 0
    assert body["choice_total"] == 1
    answers = session.scalars(select(Answer)).all()
    assert len(answers) == 2
    for answer in answers:
        assert answer.answer_text is None
        assert answer.selected_option_id is None
    choice_answer = next(
        answer
        for answer in answers
        if answer.question_id == _questions(session, test_id)[QUESTION_CHOICE].id
    )
    assert choice_answer.is_correct_auto is False


def test_open_only_test_has_zero_choice_total(
    api: TestClient,
    auth: dict[str, str],
    material: dict[str, object],
    fake_ai: FakeAI,
    session: Session,
) -> None:
    fake_ai.quiz = _open_quiz()
    test_id = generate_test(
        api, auth, str(material["id"]), choice_count=0, open_count=1
    )["test_id"]
    opened = _questions(session, test_id)[QUESTION_OPEN]

    response = _submit(
        api, auth, test_id, [{"question_id": opened.id, "answer_text": OPEN_TEXT}]
    )

    assert response.status_code == 201
    body = response.json()
    assert body["choice_total"] == 0
    assert body["choice_correct"] == 0


def test_foreign_test_is_not_found(
    api: TestClient,
    auth: dict[str, str],
    other_auth: dict[str, str],
    material: dict[str, object],
    session: Session,
) -> None:
    test_id = generate_test(api, auth, str(material["id"]))["test_id"]

    response = _submit(api, other_auth, test_id, [])

    assert response.status_code == 404
    assert session.scalars(select(Attempt)).all() == []


def test_unknown_test_is_not_found(api: TestClient, auth: dict[str, str]) -> None:
    response = _submit(api, auth, "missing-test", [])

    assert response.status_code == 404


def test_repeated_submission_stores_separate_attempts(
    api: TestClient,
    auth: dict[str, str],
    material: dict[str, object],
    session: Session,
) -> None:
    test_id = generate_test(api, auth, str(material["id"]))["test_id"]

    first = _submit(api, auth, test_id, []).json()["attempt_id"]
    second = _submit(api, auth, test_id, []).json()["attempt_id"]

    assert first != second
    assert len(session.scalars(select(Attempt)).all()) == 2


def test_submission_does_not_need_model(
    api: TestClient,
    auth: dict[str, str],
    material: dict[str, object],
    fake_ai: FakeAI,
) -> None:
    test_id = generate_test(api, auth, str(material["id"]))["test_id"]
    fake_ai.error = QuizGenerationError("model is down")

    response = _submit(api, auth, test_id, [])

    assert response.status_code == 201


def test_check_stores_scores_and_feedback(
    api: TestClient,
    auth: dict[str, str],
    material: dict[str, object],
    fake_ai: FakeAI,
    session: Session,
) -> None:
    test_id = generate_test(api, auth, str(material["id"]))["test_id"]
    opened = _questions(session, test_id)[QUESTION_OPEN]
    attempt_id = _submit(
        api, auth, test_id, [{"question_id": opened.id, "answer_text": OPEN_TEXT}]
    ).json()["attempt_id"]

    response = api.post(f"/attempts/{attempt_id}/check", headers=auth)

    assert response.status_code == 200
    body = response.json()
    assert body["attempt_id"] == attempt_id
    assert body["status"] == ATTEMPT_CHECKED
    assert body["answers"] == [
        {"question_id": opened.id, "score": 80.0, "feedback": "Смысл передан верно"}
    ]
    assert fake_ai.evaluate_calls and len(fake_ai.evaluate_calls[0]) == 1

    session.rollback()
    stored = session.get(Attempt, attempt_id)
    assert stored is not None
    assert stored.status == ATTEMPT_CHECKED
    assert stored.checked_at is not None
    answer = next(item for item in stored.answers if item.question_id == opened.id)
    assert float(answer.llm_score or 0) == 80.0
    assert answer.llm_feedback == "Смысл передан верно"


def test_empty_answer_is_not_sent_to_model(
    api: TestClient,
    auth: dict[str, str],
    material: dict[str, object],
    fake_ai: FakeAI,
    session: Session,
) -> None:
    test_id = generate_test(api, auth, str(material["id"]))["test_id"]
    opened = _questions(session, test_id)[QUESTION_OPEN]
    attempt_id = _submit(
        api, auth, test_id, [{"question_id": opened.id, "answer_text": "   "}]
    ).json()["attempt_id"]

    response = api.post(f"/attempts/{attempt_id}/check", headers=auth)

    assert response.status_code == 200
    result = response.json()["answers"][0]
    assert result["score"] == 0
    assert result["feedback"]
    assert fake_ai.evaluate_calls == []


def test_model_error_keeps_attempt_untouched(
    api: TestClient,
    auth: dict[str, str],
    material: dict[str, object],
    fake_ai: FakeAI,
    session: Session,
) -> None:
    test_id = generate_test(api, auth, str(material["id"]))["test_id"]
    opened = _questions(session, test_id)[QUESTION_OPEN]
    attempt_id = _submit(
        api, auth, test_id, [{"question_id": opened.id, "answer_text": OPEN_TEXT}]
    ).json()["attempt_id"]
    fake_ai.error = QuizGenerationError("model is down")

    response = api.post(f"/attempts/{attempt_id}/check", headers=auth)

    assert response.status_code == 502
    session.rollback()
    stored = session.get(Attempt, attempt_id)
    assert stored is not None
    assert stored.status == ATTEMPT_SUBMITTED
    assert stored.checked_at is None
    answer = next(item for item in stored.answers if item.question_id == opened.id)
    assert answer.llm_score is None
    assert answer.llm_feedback is None


def test_malformed_evaluation_is_rejected(
    api: TestClient,
    auth: dict[str, str],
    material: dict[str, object],
    fake_ai: FakeAI,
    session: Session,
) -> None:
    fake_ai.quiz = _open_quiz(count=2)
    test_id = generate_test(
        api, auth, str(material["id"]), choice_count=0, open_count=2
    )["test_id"]
    questions = question_rows(session, test_id)
    attempt_id = _submit(
        api,
        auth,
        test_id,
        [
            {"question_id": questions[0].id, "answer_text": OPEN_TEXT},
            {"question_id": questions[1].id, "answer_text": OPEN_TEXT},
        ],
    ).json()["attempt_id"]
    fake_ai.evaluations = [AnswerEvaluation(score=10, feedback="Один ответ из двух")]

    response = api.post(f"/attempts/{attempt_id}/check", headers=auth)

    assert response.status_code == 502
    session.rollback()
    stored = session.get(Attempt, attempt_id)
    assert stored is not None
    assert stored.status == ATTEMPT_SUBMITTED


def test_repeated_check_overwrites_scores(
    api: TestClient,
    auth: dict[str, str],
    material: dict[str, object],
    fake_ai: FakeAI,
    session: Session,
) -> None:
    test_id = generate_test(api, auth, str(material["id"]))["test_id"]
    opened = _questions(session, test_id)[QUESTION_OPEN]
    attempt_id = _submit(
        api, auth, test_id, [{"question_id": opened.id, "answer_text": OPEN_TEXT}]
    ).json()["attempt_id"]

    api.post(f"/attempts/{attempt_id}/check", headers=auth)
    fake_ai.evaluations = [AnswerEvaluation(score=100, feedback="Отлично")]
    second = api.post(f"/attempts/{attempt_id}/check", headers=auth)

    assert second.status_code == 200
    assert second.json()["answers"][0]["score"] == 100.0
    session.rollback()
    stored = session.get(Attempt, attempt_id)
    assert stored is not None
    answer = next(item for item in stored.answers if item.question_id == opened.id)
    assert float(answer.llm_score or 0) == 100.0
    assert answer.llm_feedback == "Отлично"


def test_foreign_attempt_check_is_not_found(
    api: TestClient,
    auth: dict[str, str],
    other_auth: dict[str, str],
    material: dict[str, object],
) -> None:
    test_id = generate_test(api, auth, str(material["id"]))["test_id"]
    attempt_id = _submit(api, auth, test_id, []).json()["attempt_id"]

    response = api.post(f"/attempts/{attempt_id}/check", headers=other_auth)

    assert response.status_code == 404


def test_history_is_isolated_and_newest_first(
    api: TestClient,
    auth: dict[str, str],
    other_auth: dict[str, str],
    material: dict[str, object],
) -> None:
    test_id = generate_test(api, auth, str(material["id"]))["test_id"]

    assert api.get("/attempts", headers=auth).json() == []

    first = _submit(api, auth, test_id, []).json()["attempt_id"]
    time.sleep(0.01)
    second = _submit(api, auth, test_id, []).json()["attempt_id"]

    history = api.get("/attempts", headers=auth)
    assert history.status_code == 200
    items = history.json()
    assert [item["id"] for item in items] == [second, first]
    assert items[0]["test_id"] == test_id
    assert items[0]["material_id"] == material["id"]
    assert items[0]["material_title"] == "Конспект"
    assert items[0]["choice_total"] == 1

    assert api.get("/attempts", headers=other_auth).json() == []


def test_detail_shows_answers_and_scores(
    api: TestClient,
    auth: dict[str, str],
    material: dict[str, object],
    session: Session,
) -> None:
    test_id = generate_test(api, auth, str(material["id"]))["test_id"]
    questions = _questions(session, test_id)
    attempt_id = _submit(
        api,
        auth,
        test_id,
        [
            {
                "question_id": questions[QUESTION_CHOICE].id,
                "selected_option_id": _option(session, questions[QUESTION_CHOICE], correct=True),
            },
            {"question_id": questions[QUESTION_OPEN].id, "answer_text": OPEN_TEXT},
        ],
    ).json()["attempt_id"]
    api.post(f"/attempts/{attempt_id}/check", headers=auth)

    response = api.get(f"/attempts/{attempt_id}", headers=auth)

    assert response.status_code == 200
    detail = response.json()
    assert set(detail) >= {
        "id",
        "test_id",
        "material_id",
        "material_title",
        "status",
        "choice_correct",
        "choice_total",
        "created_at",
        "checked_at",
        "summary",
        "questions",
    }
    assert detail["status"] == ATTEMPT_CHECKED
    choice, opened = detail["questions"]
    assert choice["type"] == QUESTION_CHOICE
    assert choice["correct_index"] == 0
    assert choice["selected_index"] == 0
    assert choice["is_correct"] is True
    assert opened["type"] == QUESTION_OPEN
    assert opened["answer_text"] == OPEN_TEXT
    assert opened["llm_score"] == 80.0
    assert opened["llm_feedback"] == "Смысл передан верно"
    assert opened["correct_index"] is None


def test_detail_of_foreign_and_unknown_attempt(
    api: TestClient,
    auth: dict[str, str],
    other_auth: dict[str, str],
    material: dict[str, object],
) -> None:
    test_id = generate_test(api, auth, str(material["id"]))["test_id"]
    attempt_id = _submit(api, auth, test_id, []).json()["attempt_id"]

    assert api.get(f"/attempts/{attempt_id}", headers=other_auth).status_code == 404
    assert api.get("/attempts/missing-attempt", headers=auth).status_code == 404
