"""Pydantic-схемы сгенерированного теста.

Схема используется и как контракт ответа модели (`with_structured_output`),
и как `response_model` эндпоинта, поэтому проверки структуры живут здесь:
модель может вернуть индекс правильного ответа вне диапазона вариантов.
"""

from pydantic import BaseModel, Field, model_validator


class Question(BaseModel):
    """Вопрос с вариантами ответов и индексом правильного."""

    text: str = Field(min_length=1, description="Формулировка вопроса")
    options: list[str] = Field(min_length=2, description="Варианты ответа")
    correct_index: int = Field(ge=0, description="Индекс правильного варианта")


class Quiz(BaseModel):
    """Результат разбора материала: краткое содержание и вопросы."""

    summary: list[str] = Field(min_length=1, description="Краткое содержание материала")
    questions: list[Question] = Field(min_length=1, description="Вопросы по материалу")

    @model_validator(mode="after")
    def _check_correct_index(self) -> "Quiz":
        """Индекс правильного ответа обязан указывать на существующий вариант."""
        for question in self.questions:
            if question.correct_index >= len(question.options):
                raise ValueError(
                    f"correct_index {question.correct_index} is out of range "
                    f"for {len(question.options)} options"
                )
        return self
