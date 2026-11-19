"""Pydantic-схемы проверки открытых ответов.

Модель возвращает оценки списком в порядке отправленных ответов: номер ответа
подставляет сервер, поэтому модель не может «перепутать» индексы.
"""

from pydantic import BaseModel, Field


class OpenAnswer(BaseModel):
    """Один ответ студента вместе с вопросом и эталоном."""

    question: str = Field(min_length=1, description="Формулировка вопроса")
    reference: str = Field(min_length=1, description="Эталонный ответ")
    answer: str = Field(default="", description="Ответ студента; может быть пустым")


class QuizCheckRequest(BaseModel):
    """Запрос проверки открытых ответов по материалу."""

    material_id: str = Field(min_length=1, description="Материал, по которому шёл тест")
    answers: list[OpenAnswer] = Field(min_length=1, description="Ответы для проверки")


class AnswerEvaluation(BaseModel):
    """Оценка одного ответа в том виде, в котором её возвращает модель."""

    score: int = Field(ge=0, le=100, description="Оценка от 0 до 100")
    feedback: str = Field(min_length=1, description="Комментарий на русском языке")


class ModelEvaluation(BaseModel):
    """Контракт ответа модели: оценки в порядке отправленных ответов."""

    evaluations: list[AnswerEvaluation] = Field(
        min_length=1, description="Оценки в порядке отправленных ответов"
    )


class CheckedAnswer(BaseModel):
    """Оценка ответа в ответе API: номер привязан к позиции в запросе."""

    index: int = Field(ge=0, description="Позиция ответа в запросе")
    score: int = Field(ge=0, le=100, description="Оценка от 0 до 100")
    feedback: str = Field(min_length=1, description="Комментарий на русском языке")


class QuizCheckResponse(BaseModel):
    """Результат проверки: по одной оценке на каждый отправленный ответ."""

    results: list[CheckedAnswer] = Field(min_length=1, description="Оценки ответов")
