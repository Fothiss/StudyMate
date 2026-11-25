"""Точка подмены языковой модели.

Транспорт (OAuth, структурированный ответ, обработка ошибок) остаётся в
`services/gigachat.py`, а сервисы работают через этот узкий фасад. В тестах он
подменяется в DI (`app.dependency_overrides[get_ai_service]`), поэтому проверки
не ходят в сеть.
"""

from app.schemas.quiz import Quiz
from app.schemas.quiz_check import AnswerEvaluation, OpenAnswer
from app.services import gigachat


class AIService:
    """Генерация теста и проверка открытых ответов средствами GigaChat."""

    def generate_quiz(
        self,
        text: str,
        *,
        choice_count: int = 5,
        open_count: int = 0,
    ) -> Quiz:
        """Генерирует тест по тексту материала."""
        return gigachat.generate_quiz(
            text, choice_count=choice_count, open_count=open_count
        )

    def evaluate_answers(
        self,
        text: str,
        answers: list[OpenAnswer],
    ) -> list[AnswerEvaluation]:
        """Оценивает открытые ответы одним запросом к модели."""
        return gigachat.evaluate_answers(text, answers)
