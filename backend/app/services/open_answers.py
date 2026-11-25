"""Проверка открытых ответов сохранённой попытки.

Пустые ответы в модель не уходят: балл за них нулевой по определению, а запрос
к GigaChat стоит до двух минут.
"""

from app.schemas.quiz_check import AnswerEvaluation, OpenAnswer
from app.services.ai import AIService
from app.services.gigachat import QuizGenerationError

EMPTY_ANSWER_FEEDBACK = (
    "Ответ не дан, поэтому балл нулевой. Сверьтесь с эталоном и попробуйте сформулировать ответ."
)


def grade_open_answers(
    text: str,
    answers: list[OpenAnswer],
    ai: AIService,
) -> list[AnswerEvaluation]:
    """Оценивает ответы в том же порядке, в котором они переданы.

    Ошибку модели пробрасывает наверх: вызывающий сам решает, каким кодом
    ответить, и не должен получить частично заполненный результат.
    """
    positions = [index for index, answer in enumerate(answers) if answer.answer.strip()]
    graded: dict[int, AnswerEvaluation] = {}
    if positions:
        grades = ai.evaluate_answers(text, [answers[index] for index in positions])
        if len(grades) != len(positions):
            raise QuizGenerationError(
                f"Model returned {len(grades)} evaluations for {len(positions)} answers"
            )
        graded = dict(zip(positions, grades, strict=True))

    return [
        graded.get(index)
        or AnswerEvaluation(score=0, feedback=EMPTY_ANSWER_FEEDBACK)
        for index in range(len(answers))
    ]
