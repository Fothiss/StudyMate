"""Полный сценарий: материал → тест → сдача → проверка → история → разбор."""

from fastapi.testclient import TestClient

from app.models.question import QUESTION_CHOICE, QUESTION_OPEN
from tests.helpers import (
    generate_test,
    option_rows,
    question_rows,
    upload_material,
)
from sqlalchemy.orm import Session


def test_full_learning_flow(api: TestClient, auth: dict[str, str], session: Session) -> None:
    material = upload_material(api, auth)

    quiz = generate_test(api, auth, str(material["id"]), choice_count=1, open_count=1)
    test_id = quiz["test_id"]

    questions = {question.type: question for question in question_rows(session, test_id)}
    choice = questions[QUESTION_CHOICE]
    correct_index = next(
        index
        for index, option in enumerate(option_rows(session, choice.id))
        if option.is_correct
    )

    submitted = api.post(
        f"/tests/{test_id}/attempts",
        json={
            "answers": [
                {"question_id": choice.id, "selected_index": correct_index},
                {
                    "question_id": questions[QUESTION_OPEN].id,
                    "answer_text": "Свет превращается в химическую энергию",
                },
            ]
        },
        headers=auth,
    )
    assert submitted.status_code == 201
    attempt_id = submitted.json()["attempt_id"]
    assert submitted.json()["choice_correct"] == 1

    checked = api.post(f"/attempts/{attempt_id}/check", headers=auth)
    assert checked.status_code == 200
    assert checked.json()["answers"][0]["score"] == 80.0

    history = api.get("/attempts", headers=auth)
    assert history.status_code == 200
    assert [item["id"] for item in history.json()] == [attempt_id]

    detail = api.get(f"/attempts/{attempt_id}", headers=auth)
    assert detail.status_code == 200
    body = detail.json()
    assert body["material_title"] == material["title"]
    assert [question["question_id"] for question in body["questions"]] == [
        choice.id,
        questions[QUESTION_OPEN].id,
    ]
    assert body["questions"][1]["llm_score"] == 80.0
