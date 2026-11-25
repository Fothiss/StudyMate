"""Pydantic-схемы попыток прохождения теста."""

from datetime import datetime

from pydantic import BaseModel, Field


class AttemptAnswerInput(BaseModel):
    """Ответ пользователя на один вопрос.

    Вопрос адресуется идентификатором, а выбор варианта — его позицией в
    списке вариантов: клиент не получает идентификаторы вариантов и не должен
    ими оперировать. Присланный `correct_index` или эталон сервер не читает —
    верность берётся из БД.
    """

    question_id: str = Field(min_length=1, description="Вопрос, к которому относится ответ")
    selected_index: int | None = Field(
        default=None,
        ge=0,
        description="Позиция выбранного варианта в списке вариантов вопроса",
    )
    answer_text: str | None = Field(default=None, description="Текст ответа на открытый вопрос")


class AttemptSubmitRequest(BaseModel):
    """Тело запроса на сдачу теста.

    Пустой список допустим: сдача без единого ответа всё равно создаёт попытку
    со строкой на каждый вопрос теста.
    """

    answers: list[AttemptAnswerInput] = Field(
        default_factory=list, description="Ответы пользователя"
    )


class AttemptAnswerRead(BaseModel):
    """Сохранённый ответ одного вопроса."""

    question_id: str
    is_correct: bool | None = Field(
        default=None, description="Верность тестового ответа; у открытого вопроса пусто"
    )
    llm_score: float | None = Field(default=None, description="Балл проверки открытого ответа")
    llm_feedback: str | None = Field(default=None, description="Комментарий проверки")


class AttemptSubmitResponse(BaseModel):
    """Результат сдачи: счёт по тестовым вопросам известен сразу."""

    attempt_id: str
    status: str
    choice_correct: int
    choice_total: int
    answers: list[AttemptAnswerRead]


class CheckedOpenAnswer(BaseModel):
    """Оценка открытого ответа после проверки моделью."""

    question_id: str
    score: float
    feedback: str


class AttemptCheckResponse(BaseModel):
    """Результат проверки открытых ответов попытки."""

    attempt_id: str
    status: str
    answers: list[CheckedOpenAnswer]


class AttemptSummaryRead(BaseModel):
    """Попытка в истории: что проходили и с каким счётом."""

    id: str
    test_id: str
    material_id: str
    material_title: str
    status: str
    choice_correct: int
    choice_total: int
    created_at: datetime
    checked_at: datetime | None


class AttemptQuestionRead(BaseModel):
    """Вопрос теста в разборе попытки: ответ, правильный вариант и оценка."""

    question_id: str
    type: str
    text: str
    options: list[str]
    correct_index: int | None = Field(
        default=None, description="Индекс правильного варианта у тестового вопроса"
    )
    selected_index: int | None = Field(
        default=None, description="Индекс выбранного варианта; пусто, если не отвечен"
    )
    answer_text: str | None = None
    reference: str | None = Field(
        default=None, description="Эталон открытого вопроса; у тестового вопроса пусто"
    )
    is_correct: bool | None = None
    llm_score: float | None = None
    llm_feedback: str | None = None


class AttemptDetailRead(AttemptSummaryRead):
    """Разбор одной попытки: краткое содержание теста и все его вопросы."""

    summary: list[str]
    questions: list[AttemptQuestionRead]
