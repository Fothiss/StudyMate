"""Сдача тестов, проверка открытых ответов и история попыток.

Два префикса (`/tests` и `/attempts`), потому что сдача относится к тесту, а
проверка и чтение — к уже созданной попытке.
"""

from fastapi import APIRouter, HTTPException, status

from app.dependencies.security import CurrentUser
from app.dependencies.services import AttemptServiceDep
from app.models.attempt import Attempt
from app.models.question import QUESTION_CHOICE, QUESTION_OPEN
from app.schemas.attempt import (
    AttemptAnswerRead,
    AttemptCheckResponse,
    AttemptDetailRead,
    AttemptQuestionRead,
    AttemptSubmitRequest,
    AttemptSubmitResponse,
    AttemptSummaryRead,
    CheckedOpenAnswer,
)
from app.services.gigachat import QuizGenerationError

tests_router = APIRouter(prefix="/tests", tags=["attempts"])
attempts_router = APIRouter(prefix="/attempts", tags=["attempts"])


@tests_router.post(
    "/{test_id}/attempts",
    response_model=AttemptSubmitResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Сдать тест",
)
def submit_attempt(
    test_id: str,
    payload: AttemptSubmitRequest,
    service: AttemptServiceDep,
    current_user: CurrentUser,
) -> AttemptSubmitResponse:
    """Сохраняет попытку и сразу оценивает её тестовые вопросы.

    Модель не вызывается, поэтому ответ приходит без ожидания. Открытые
    ответы проверяются отдельным запросом.
    """
    attempt = service.submit(current_user, test_id, payload.answers)
    if attempt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found",
        )
    return _submit_view(attempt)


@attempts_router.post(
    "/{attempt_id}/check",
    response_model=AttemptCheckResponse,
    summary="Проверить открытые ответы попытки",
)
def check_attempt(
    attempt_id: str,
    service: AttemptServiceDep,
    current_user: CurrentUser,
) -> AttemptCheckResponse:
    """Проверяет открытые ответы попытки по эталонам из БД.

    Повторный вызов перезаписывает сохранённые оценки: проверка всегда идёт
    заново, а не отдаёт прошлый результат.
    """
    try:
        attempt = service.check(current_user, attempt_id)
    except QuizGenerationError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to evaluate answers",
        ) from error
    if attempt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found",
        )
    return _check_view(attempt)


@attempts_router.get(
    "",
    response_model=list[AttemptSummaryRead],
    summary="История попыток",
)
def list_attempts(
    service: AttemptServiceDep,
    current_user: CurrentUser,
) -> list[AttemptSummaryRead]:
    """Отдаёт только попытки текущего пользователя, новые сверху."""
    return [_summary_view(attempt) for attempt in service.list(current_user)]


@attempts_router.get(
    "/{attempt_id}",
    response_model=AttemptDetailRead,
    summary="Разбор попытки",
)
def read_attempt(
    attempt_id: str,
    service: AttemptServiceDep,
    current_user: CurrentUser,
) -> AttemptDetailRead:
    """Показывает вопросы теста, данные ответы и сохранённые оценки."""
    attempt = service.get(current_user, attempt_id)
    if attempt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found",
        )
    return _detail_view(attempt)


def _summary_view(attempt: Attempt) -> AttemptSummaryRead:
    """Попытка в истории: тест, материал и счёт по тестовым вопросам."""
    test = attempt.test
    return AttemptSummaryRead(
        id=attempt.id,
        test_id=test.id,
        material_id=test.material_id,
        material_title=test.material.title,
        status=attempt.status,
        choice_correct=attempt.choice_correct,
        choice_total=attempt.choice_total,
        created_at=attempt.created_at,
        checked_at=attempt.checked_at,
    )


def _submit_view(attempt: Attempt) -> AttemptSubmitResponse:
    """Результат сдачи в порядке вопросов теста."""
    by_question = {answer.question_id: answer for answer in attempt.answers}
    answers = []
    for question in attempt.test.questions:
        answer = by_question.get(question.id)
        if answer is None:
            continue
        answers.append(
            AttemptAnswerRead(
                question_id=question.id,
                is_correct=answer.is_correct_auto,
                llm_score=answer.llm_score,
                llm_feedback=answer.llm_feedback,
            )
        )
    return AttemptSubmitResponse(
        attempt_id=attempt.id,
        status=attempt.status,
        choice_correct=attempt.choice_correct,
        choice_total=attempt.choice_total,
        answers=answers,
    )


def _check_view(attempt: Attempt) -> AttemptCheckResponse:
    """Оценки открытых ответов в порядке вопросов теста."""
    by_question = {answer.question_id: answer for answer in attempt.answers}
    results = []
    for question in attempt.test.questions:
        if question.type != QUESTION_OPEN:
            continue
        answer = by_question.get(question.id)
        if answer is None:
            continue
        results.append(
            CheckedOpenAnswer(
                question_id=question.id,
                score=float(answer.llm_score or 0),
                feedback=answer.llm_feedback or "",
            )
        )
    return AttemptCheckResponse(
        attempt_id=attempt.id,
        status=attempt.status,
        answers=results,
    )


def _detail_view(attempt: Attempt) -> AttemptDetailRead:
    """Разбор попытки: по вопросу на строку, в порядке теста."""
    by_question = {answer.question_id: answer for answer in attempt.answers}
    questions = []
    for question in attempt.test.questions:
        answer = by_question.get(question.id)
        options = [option.text for option in question.options]
        correct_index = None
        selected_index = None
        reference = None
        if question.type == QUESTION_CHOICE:
            correct_index = next(
                (
                    index
                    for index, option in enumerate(question.options)
                    if option.is_correct
                ),
                None,
            )
            if answer is not None and answer.selected_option_id is not None:
                selected_index = next(
                    (
                        index
                        for index, option in enumerate(question.options)
                        if option.id == answer.selected_option_id
                    ),
                    None,
                )
        elif question.rubric is not None:
            reference = question.rubric.reference_answer
        questions.append(
            AttemptQuestionRead(
                question_id=question.id,
                type=question.type,
                text=question.text,
                options=options,
                correct_index=correct_index,
                selected_index=selected_index,
                answer_text=answer.answer_text if answer is not None else None,
                reference=reference,
                is_correct=answer.is_correct_auto if answer is not None else None,
                llm_score=answer.llm_score if answer is not None else None,
                llm_feedback=answer.llm_feedback if answer is not None else None,
            )
        )
    return AttemptDetailRead(
        **_summary_view(attempt).model_dump(),
        summary=attempt.test.summary,
        questions=questions,
    )
