"""Pydantic-схемы сгенерированного теста.

Первая половина файла — контракт ответа модели (`with_structured_output`):
именно здесь живут проверки структуры, потому что модель может вернуть индекс
правильного ответа вне диапазона вариантов. Вторая половина — контракт ответа
API: он собирается из сохранённого теста и описывает только то, что нужно
клиенту, чтобы показать вопросы и сдать их.
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


class ChoiceQuestionRead(BaseModel):
    """Тестовый вопрос в ответе API: то, что нужно, чтобы ответить."""

    question_id: str = Field(description="Идентификатор сохранённого вопроса")
    kind: Literal["choice"] = Field(default="choice", description="Тип вопроса: тестовый")
    text: str = Field(min_length=1, description="Формулировка вопроса")
    options: list[str] = Field(min_length=2, description="Варианты ответа")


class OpenQuestionRead(BaseModel):
    """Открытый вопрос в ответе API: без эталона, он нужен только серверу."""

    question_id: str = Field(description="Идентификатор сохранённого вопроса")
    kind: Literal["open"] = Field(default="open", description="Тип вопроса: открытый")
    text: str = Field(min_length=1, description="Формулировка вопроса")


QuestionRead = Annotated[
    ChoiceQuestionRead | OpenQuestionRead,
    Field(discriminator="kind", description="Вопрос одного из поддерживаемых типов"),
]


class TestRead(BaseModel):
    """Тест в ответе API, собранный из сохранённых строк.

    `question_id` нужен клиенту, чтобы сдавать ответы адресно, а не по
    позиции: порядок вопросов может измениться только вместе с тестом, но
    ссылка на вопрос от него не зависит.
    """

    test_id: str = Field(description="Идентификатор сохранённого теста")
    summary: list[str] = Field(min_length=1, description="Краткое содержание материала")
    questions: list[QuestionRead] = Field(min_length=1, description="Вопросы теста")


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
