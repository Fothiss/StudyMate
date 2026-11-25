"""Проверка открытых ответов теста.

Эндпоинт устарел: проверка идёт по сохранённой попытке
(`POST /attempts/{attempt_id}/check`), где эталоны берутся из БД. Здесь он
остаётся, пока UI не перешёл на попытки, и использует тот же код проверки.
"""

from fastapi import APIRouter, HTTPException, status

from app.dependencies.security import CurrentUser
from app.dependencies.services import AIServiceDep, MaterialServiceDep
from app.schemas.quiz_check import (
    CheckedAnswer,
    QuizCheckRequest,
    QuizCheckResponse,
)
from app.services.gigachat import QuizGenerationError
from app.services.open_answers import grade_open_answers

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.post(
    "/check",
    response_model=QuizCheckResponse,
    summary="Проверить открытые ответы",
    deprecated=True,
)
def check_open_answers(
    payload: QuizCheckRequest,
    current_user: CurrentUser,
    service: MaterialServiceDep,
    ai: AIServiceDep,
) -> QuizCheckResponse:
    """Оценивает ответы через GigaChat, пустые ответы не отправляя в модель."""
    material = service.get(current_user, payload.material_id)
    if material is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found",
        )
    if not material.extracted_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Material has no extracted text",
        )

    try:
        grades = grade_open_answers(material.extracted_text, payload.answers, ai)
    except QuizGenerationError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to evaluate answers",
        ) from error

    return QuizCheckResponse(
        results=[
            CheckedAnswer(index=index, score=grade.score, feedback=grade.feedback)
            for index, grade in enumerate(grades)
        ]
    )
