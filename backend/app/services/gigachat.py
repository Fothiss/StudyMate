"""Клиент GigaChat и генерация теста по тексту материала."""

from functools import lru_cache

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat import GigaChat

from app.core.config import settings
from app.schemas.quiz import Quiz
from app.schemas.quiz_check import AnswerEvaluation, ModelEvaluation, OpenAnswer
from app.services.prompts.quiz import (
    MATERIAL_HEADER,
    QUIZ_SYSTEM_PROMPT,
    build_quiz_instructions,
)
from app.services.prompts.quiz_check import (
    ANSWERS_HEADER,
    CHECK_INSTRUCTIONS,
    CHECK_SYSTEM_PROMPT,
    MATERIAL_HEADER as CHECK_MATERIAL_HEADER,
)


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


def generate_quiz(text: str, choice_count: int = 5, open_count: int = 0) -> Quiz:
    """Генерирует краткое содержание и вопросы по тексту материала.

    Текст передаётся сообщением, поэтому структура запрашивается обычным
    `with_structured_output`: встроенная функция чтения файлов здесь не нужна.
    """
    client = get_client()
    chain = client.with_structured_output(Quiz)
    instructions = build_quiz_instructions(choice_count, open_count)
    messages = [
        SystemMessage(content=QUIZ_SYSTEM_PROMPT),
        HumanMessage(content=f"{instructions}\n\n{MATERIAL_HEADER}\n{text}"),
    ]

    try:
        quiz = chain.invoke(messages)
    except Exception as error:  # noqa: BLE001 — любая ошибка модели или парсинга
        raise QuizGenerationError(str(error)) from error

    if not isinstance(quiz, Quiz):
        raise QuizGenerationError("Model returned no quiz")

    return quiz


def evaluate_answers(text: str, answers: list[OpenAnswer]) -> list[AnswerEvaluation]:
    """Оценивает открытые ответы одним запросом к модели.

    Ответы уходят списком: у физлица один поток, поэтому отдельный вызов на
    каждый ответ занял бы столько же минут, сколько ответов в тесте.
    """
    if not answers:
        return []

    client = get_client()
    chain = client.with_structured_output(ModelEvaluation)

    blocks = [
        f"{position}. Вопрос: {answer.question}\n"
        f"Эталон: {answer.reference}\n"
        f"Ответ студента: {answer.answer.strip()}"
        for position, answer in enumerate(answers, start=1)
    ]
    instructions = CHECK_INSTRUCTIONS.format(count=len(answers))
    messages = [
        SystemMessage(content=CHECK_SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"{instructions}\n\n{ANSWERS_HEADER}\n"
                + "\n\n".join(blocks)
                + f"\n\n{CHECK_MATERIAL_HEADER}\n{text}"
            )
        ),
    ]

    try:
        evaluation = chain.invoke(messages)
    except Exception as error:  # noqa: BLE001 — любая ошибка модели или парсинга
        raise QuizGenerationError(str(error)) from error

    if not isinstance(evaluation, ModelEvaluation):
        raise QuizGenerationError("Model returned no evaluation")
    if len(evaluation.evaluations) != len(answers):
        raise QuizGenerationError(
            f"Model returned {len(evaluation.evaluations)} evaluations "
            f"for {len(answers)} answers"
        )

    return evaluation.evaluations
