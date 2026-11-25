"""Генерация теста: сохранение в БД и обратная совместимость ответа."""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.question import QUESTION_OPEN
from app.models.test import Test
from app.services.gigachat import QuizGenerationError
from tests.helpers import (
    FakeAI,
    generate_test,
    question_rows,
    upload_material,
)


def test_generation_stores_test_with_questions(
    api: TestClient,
    auth: dict[str, str],
    material: dict[str, object],
    session: Session,
) -> None:
    body = generate_test(api, auth, str(material["id"]), choice_count=1, open_count=1)

    stored = session.scalars(select(Test)).all()
    assert len(stored) == 1
    assert stored[0].id == body["test_id"]
    assert stored[0].material_id == material["id"]
    assert stored[0].generation_params == {"choice_count": 1, "open_count": 1}

    questions = question_rows(session, stored[0].id)
    assert [question.order_index for question in questions] == [0, 1]
    open_question = questions[1]
    assert open_question.type == QUESTION_OPEN
    assert open_question.rubric is not None
    assert open_question.rubric.reference_answer


def test_generation_response_carries_question_ids(
    api: TestClient,
    auth: dict[str, str],
    material: dict[str, object],
    session: Session,
) -> None:
    body = generate_test(api, auth, str(material["id"]))

    stored = question_rows(session, body["test_id"])
    assert [question["question_id"] for question in body["questions"]] == [
        question.id for question in stored
    ]

    assert set(body) >= {"summary", "questions", "test_id"}
    choice, open_question = body["questions"]
    assert choice["kind"] == "choice"
    assert len(choice["options"]) == 3
    assert open_question["kind"] == "open"

    # Правильные ответы и эталоны живут в БД: до сдачи клиент их не получает.
    assert "correct_index" not in choice
    assert "reference" not in open_question


def test_each_generation_stores_new_test(
    api: TestClient,
    auth: dict[str, str],
    material: dict[str, object],
    session: Session,
) -> None:
    first = generate_test(api, auth, str(material["id"]))
    second = generate_test(api, auth, str(material["id"]))

    assert first["test_id"] != second["test_id"]
    assert len(session.scalars(select(Test)).all()) == 2


def test_generation_failure_stores_nothing(
    api: TestClient,
    auth: dict[str, str],
    material: dict[str, object],
    fake_ai: FakeAI,
    session: Session,
) -> None:
    fake_ai.error = QuizGenerationError("model is down")

    response = api.post(
        f"/materials/{material['id']}/quiz",
        json={"choice_count": 1, "open_count": 0},
        headers=auth,
    )

    assert response.status_code == 502
    assert session.scalars(select(Test)).all() == []


def test_foreign_material_is_not_found(
    api: TestClient,
    other_auth: dict[str, str],
    material: dict[str, object],
    session: Session,
) -> None:
    response = api.post(
        f"/materials/{material['id']}/quiz",
        json={"choice_count": 1, "open_count": 0},
        headers=other_auth,
    )

    assert response.status_code == 404
    assert session.scalars(select(Test)).all() == []


def test_generation_requires_auth(api: TestClient, material: dict[str, object]) -> None:
    response = api.post(
        f"/materials/{material['id']}/quiz",
        json={"choice_count": 1, "open_count": 0},
    )

    assert response.status_code == 401


def test_material_without_quiz_request_returns_422(
    api: TestClient,
    auth: dict[str, str],
    material: dict[str, object],
) -> None:
    response = api.post(
        f"/materials/{material['id']}/quiz",
        json={"choice_count": 0, "open_count": 0},
        headers=auth,
    )

    assert response.status_code == 422


def test_uploaded_material_is_readable(
    api: TestClient,
    auth: dict[str, str],
) -> None:
    material = upload_material(api, auth, title="Второй конспект")

    response = api.get(f"/materials/{material['id']}", headers=auth)

    assert response.status_code == 200
    assert response.json()["title"] == "Второй конспект"
