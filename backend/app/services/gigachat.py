"""Клиент GigaChat и генерация теста по тексту материала."""

from functools import lru_cache

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat import GigaChat

from app.core.config import settings
from app.schemas.quiz import Quiz
from app.services.prompts.quiz import MATERIAL_HEADER, QUIZ_INSTRUCTIONS, QUIZ_SYSTEM_PROMPT


class QuizGenerationError(Exception):
    """Модель недоступна, не настроена или вернула непригодную структуру."""


@lru_cache
def get_client() -> GigaChat:
    """Клиент на процесс: конструктор `GigaChat` проходит OAuth."""
    if not settings.gigachat_credentials:
        raise QuizGenerationError("GIGACHAT_CREDENTIALS is not configured")

    return GigaChat(
        credentials=settings.gigachat_credentials,
        scope=settings.gigachat_scope,
        model=settings.gigachat_model,
        timeout=settings.gigachat_timeout,
        max_retries=1,
        verify_ssl_certs=settings.gigachat_verify_ssl,
    )


def generate_quiz(text: str) -> Quiz:
    """Генерирует краткое содержание и вопросы по тексту материала.

    Текст передаётся сообщением, поэтому структура запрашивается обычным
    `with_structured_output`: встроенная функция чтения файлов здесь не нужна.
    """
    client = get_client()
    chain = client.with_structured_output(Quiz)
    messages = [
        SystemMessage(content=QUIZ_SYSTEM_PROMPT),
        HumanMessage(content=f"{QUIZ_INSTRUCTIONS}\n\n{MATERIAL_HEADER}\n{text}"),
    ]

    try:
        quiz = chain.invoke(messages)
    except Exception as error:  # noqa: BLE001 — любая ошибка модели или парсинга
        raise QuizGenerationError(str(error)) from error

    if not isinstance(quiz, Quiz):
        raise QuizGenerationError("Model returned no quiz")

    return quiz
