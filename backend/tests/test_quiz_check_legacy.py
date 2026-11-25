"""Устаревший `POST /quiz/check`: поведение сохраняется до перехода UI."""

from fastapi.testclient import TestClient

from app.services.gigachat import QuizGenerationError
from tests.helpers import FakeAI


def _payload(material_id: object, answer: str = "Свет превращается в энергию") -> dict:
    return {
        "material_id": material_id,
        "answers": [
            {
                "question": "Что такое фотосинтез?",
                "reference": "Процесс превращения световой энергии в химическую.",
                "answer": answer,
            }
        ],
    }


def test_check_returns_score(
    api: TestClient,
    auth: dict[str, str],
    material: dict[str, object],
) -> None:
    response = api.post("/quiz/check", json=_payload(material["id"]), headers=auth)

    assert response.status_code == 200
    assert response.json()["results"] == [
        {"index": 0, "score": 80, "feedback": "Смысл передан верно"}
    ]


def test_empty_answer_is_not_sent_to_model(
    api: TestClient,
    auth: dict[str, str],
    material: dict[str, object],
    fake_ai: FakeAI,
) -> None:
    response = api.post("/quiz/check", json=_payload(material["id"], ""), headers=auth)

    assert response.status_code == 200
    result = response.json()["results"][0]
    assert result["score"] == 0
    assert result["feedback"]
    assert fake_ai.evaluate_calls == []


def test_model_error_returns_502(
    api: TestClient,
    auth: dict[str, str],
    material: dict[str, object],
    fake_ai: FakeAI,
) -> None:
    fake_ai.error = QuizGenerationError("model is down")

    response = api.post("/quiz/check", json=_payload(material["id"]), headers=auth)

    assert response.status_code == 502


def test_foreign_material_is_not_found(
    api: TestClient,
    other_auth: dict[str, str],
    material: dict[str, object],
) -> None:
    response = api.post("/quiz/check", json=_payload(material["id"]), headers=other_auth)

    assert response.status_code == 404
