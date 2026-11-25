"""Помощники тестов: модель-заглушка, данные и запросы к API."""

from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.material import Material
from app.models.question import ClosedQuestionOption, Question
from app.models.test import Test
from app.models.user import User
from app.schemas.quiz import ChoiceQuestion, OpenQuestion, Quiz
from app.schemas.quiz_check import AnswerEvaluation, OpenAnswer
from app.services.quiz_storage import build_test
from tests.pdf import build_pdf

MATERIAL_TEXT = (
    "Photosynthesis converts light energy into chemical energy stored in glucose. "
    "Chlorophyll absorbs the light inside the chloroplast."
)
PASSWORD = "secret123"
QUIZ_SUMMARY = ["Фотосинтез превращает свет в химическую энергию"]


def default_quiz() -> Quiz:
    """Тест из двух вопросов: один с вариантами, один открытый."""
    return Quiz(
        summary=QUIZ_SUMMARY,
        questions=[
            ChoiceQuestion(
                kind="choice",
                text="Что запасает энергию?",
                options=["Глюкозу", "Кислород", "Воду"],
                correct_index=0,
            ),
            OpenQuestion(
                kind="open",
                text="Что такое фотосинтез?",
                reference="Процесс превращения световой энергии в химическую.",
            ),
        ],
    )


class FakeAI:
    """Модель-заглушка: отдаёт заданный тест и заданные оценки."""

    def __init__(
        self,
        quiz: Quiz | None = None,
        evaluations: list[AnswerEvaluation] | None = None,
        error: Exception | None = None,
    ) -> None:
        self.quiz = quiz if quiz is not None else default_quiz()
        self.evaluations = evaluations
        self.error = error
        self.generate_calls = 0
        self.evaluate_calls: list[list[OpenAnswer]] = []

    def generate_quiz(
        self,
        text: str,
        *,
        choice_count: int = 5,
        open_count: int = 0,
    ) -> Quiz:
        self.generate_calls += 1
        if self.error is not None:
            raise self.error
        return self.quiz

    def evaluate_answers(
        self,
        text: str,
        answers: list[OpenAnswer],
    ) -> list[AnswerEvaluation]:
        self.evaluate_calls.append(list(answers))
        if self.error is not None:
            raise self.error
        if self.evaluations is not None:
            return list(self.evaluations)
        return [
            AnswerEvaluation(score=80, feedback="Смысл передан верно")
            for _ in answers
        ]


def register_and_login(client: TestClient, username: str) -> dict[str, str]:
    """Возвращает заголовок авторизации для нового пользователя."""
    client.post("/auth/register", json={"username": username, "password": PASSWORD})
    response = client.post(
        "/auth/login", data={"username": username, "password": PASSWORD}
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def upload_material(
    client: TestClient,
    headers: dict[str, str],
    title: str = "Конспект",
) -> dict[str, Any]:
    """Загружает материал и возвращает его карточку."""
    response = client.post(
        "/materials",
        data={"title": title},
        files={"file": ("guide.pdf", build_pdf(MATERIAL_TEXT), "application/pdf")},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def generate_test(
    client: TestClient,
    headers: dict[str, str],
    material_id: str,
    *,
    choice_count: int = 1,
    open_count: int = 1,
) -> dict[str, Any]:
    """Генерирует тест через API и возвращает тело ответа."""
    response = client.post(
        f"/materials/{material_id}/quiz",
        json={"choice_count": choice_count, "open_count": open_count},
        headers=headers,
    )
    assert response.status_code == 200, response.text
    return response.json()


def question_rows(session: Session, test_id: str) -> list[Question]:
    """Вопросы теста в порядке `order_index`."""
    statement = (
        select(Question)
        .where(Question.test_id == test_id)
        .order_by(Question.order_index)
    )
    return list(session.scalars(statement))


def option_rows(session: Session, question_id: str) -> list[ClosedQuestionOption]:
    """Варианты тестового вопроса в порядке `order_index`."""
    statement = (
        select(ClosedQuestionOption)
        .where(ClosedQuestionOption.question_id == question_id)
        .order_by(ClosedQuestionOption.order_index)
    )
    return list(session.scalars(statement))


def make_user(session: Session, username: str) -> User:
    """Создаёт пользователя напрямую, без прохождения регистрации."""
    user = User(username=username, password_hash="not-a-real-hash")
    session.add(user)
    session.flush()
    return user


def make_material(session: Session, user: User) -> Material:
    """Создаёт материал с готовым текстом."""
    material = Material(
        user_id=user.id,
        title="Конспект",
        filename="guide.pdf",
        file_path="materials/probe/guide.pdf",
        extracted_text=MATERIAL_TEXT,
        extraction_status="ready",
    )
    session.add(material)
    session.flush()
    return material


def store_test(
    session: Session,
    user: User,
    material: Material,
    quiz: Quiz | None = None,
) -> Test:
    """Сохраняет тест по ответу модели, минуя API."""
    test = build_test(
        quiz if quiz is not None else default_quiz(),
        user_id=user.id,
        material_id=material.id,
        generation_params={"choice_count": 1, "open_count": 1},
    )
    session.add(test)
    session.commit()
    return test
