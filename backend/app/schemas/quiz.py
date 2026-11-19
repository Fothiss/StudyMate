"""Pydantic-схемы сгенерированного теста.

Схема используется и как контракт ответа модели (`with_structured_output`),
и как `response_model` эндпоинта, поэтому проверки структуры живут здесь:
модель может вернуть индекс правильного ответа вне диапазона вариантов.
"""

from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator

#: Верхние границы запроса: больше одного вопроса за раз не просим,
#: иначе ответ модели перестаёт помещаться в её собственный лимит.
MAX_CHOICE_QUESTIONS = 15
MAX_OPEN_QUESTIONS = 10


class ChoiceQuestion(BaseModel):
    """Вопрос с вариантами ответов и индексом правильного."""

    kind: Literal["choice"] = Field(description="Тип вопроса: тестовый")
    text: str = Field(min_length=1, description="Формулировка вопроса")
    options: list[str] = Field(min_length=2, description="Варианты ответа")
    correct_index: int = Field(ge=0, description="Индекс правильного варианта")


class OpenQuestion(BaseModel):
    """Открытый вопрос с эталонным ответом для проверки."""

    kind: Literal["open"] = Field(description="Тип вопроса: открытый")
    text: str = Field(min_length=1, description="Формулировка вопроса")
    reference: str = Field(
        min_length=1,
        description="Эталонный ответ, по которому проверяется ответ пользователя",
    )


Question = Annotated[
    ChoiceQuestion | OpenQuestion,
    Field(discriminator="kind", description="Вопрос одного из поддерживаемых типов"),
]


class Quiz(BaseModel):
    """Результат разбора материала: краткое содержание и вопросы."""

    summary: list[str] = Field(min_length=1, description="Краткое содержание материала")
    questions: list[Question] = Field(min_length=1, description="Вопросы по материалу")

    @model_validator(mode="after")
    def _check_correct_index(self) -> "Quiz":
        """Индекс правильного ответа обязан указывать на существующий вариант."""
        for question in self.questions:
            if isinstance(question, ChoiceQuestion) and question.correct_index >= len(
                question.options
            ):
                raise ValueError(
                    f"correct_index {question.correct_index} is out of range "
                    f"for {len(question.options)} options"
                )
        return self


class QuizRequest(BaseModel):
    """Параметры генерации: сколько вопросов каждого типа нужно."""

    choice_count: int = Field(
        default=5,
        ge=0,
        le=MAX_CHOICE_QUESTIONS,
        description="Сколько тестовых вопросов сгенерировать",
    )
    open_count: int = Field(
        default=0,
        ge=0,
        le=MAX_OPEN_QUESTIONS,
        description="Сколько открытых вопросов сгенерировать",
    )

    @model_validator(mode="after")
    def _check_total(self) -> "QuizRequest":
        """Хотя бы один вопрос должен быть запрошен."""
        if self.choice_count + self.open_count == 0:
            raise ValueError("At least one question must be requested")
        return self
