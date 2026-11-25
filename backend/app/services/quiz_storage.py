"""Конвертация ответа модели в строки теста.

Схема модели (`Quiz`) и схема хранения — разные вещи: здесь `kind` становится
`type`, `correct_index` — флагом на варианте, а `reference` — эталоном. Имена
полей модели наружу и в БД не протекают.
"""

from typing import Any

from app.models.question import (
    QUESTION_CHOICE,
    QUESTION_OPEN,
    ClosedQuestionOption,
    OpenQuestionRubric,
    Question,
)
from app.models.test import Test
from app.schemas.quiz import ChoiceQuestion, OpenQuestion, Quiz


def build_test(
    quiz: Quiz,
    *,
    user_id: str,
    material_id: str,
    generation_params: dict[str, Any],
) -> Test:
    """Собирает тест с вопросами, вариантами и эталонами.

    Порядок вопросов фиксируется `order_index`: попытка ссылается на этот же
    тест, поэтому разбор позже покажет те же вопросы в том же порядке.
    """
    test = Test(
        user_id=user_id,
        material_id=material_id,
        summary=quiz.summary,
        generation_params=generation_params,
    )
    for order_index, question in enumerate(quiz.questions):
        test.questions.append(build_question(question, order_index))
    return test


def build_question(question: ChoiceQuestion | OpenQuestion, order_index: int) -> Question:
    """Собирает вопрос нужного типа вместе с его ответными данными."""
    if isinstance(question, ChoiceQuestion):
        row = Question(
            type=QUESTION_CHOICE,
            order_index=order_index,
            text=question.text,
        )
        for option_index, option in enumerate(question.options):
            row.options.append(
                ClosedQuestionOption(
                    text=option,
                    is_correct=option_index == question.correct_index,
                    order_index=option_index,
                )
            )
        return row

    row = Question(
        type=QUESTION_OPEN,
        order_index=order_index,
        text=question.text,
    )
    row.rubric = OpenQuestionRubric(reference_answer=question.reference)
    return row
