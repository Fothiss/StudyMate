"""Проверка открытых ответов теста."""

from fastapi import APIRouter, HTTPException, status

from app.dependencies.security import CurrentUser
from app.dependencies.services import MaterialServiceDep
from app.schemas.quiz_check import (
    AnswerEvaluation,
    CheckedAnswer,
    QuizCheckRequest,
    QuizCheckResponse,
)
from app.services import gigachat as gigachat_service
from app.services.gigachat import QuizGenerationError

router = APIRouter(prefix="/quiz", tags=["quiz"])

EMPTY_ANSWER_FEEDBACK = (
    "Ответ не дан, поэтому балл нулевой. Сверьтесь с эталоном и попробуйте сформулировать ответ."
)


@router.post(
    "/check",
    response_model=QuizCheckResponse,
    summary="Проверить открытые ответы",
)
def check_open_answers(
    payload: QuizCheckRequest,
    current_user: CurrentUser,
    service: MaterialServiceDep,
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

    filled = [
        (index, answer)
        for index, answer in enumerate(payload.answers)
        if answer.answer.strip()
    ]

    evaluated: dict[int, AnswerEvaluation] = {}
    if filled:
        try:
            grades = gigachat_service.evaluate_answers(
                material.extracted_text,
                [answer for _, answer in filled],
            )
        except QuizGenerationError as error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to evaluate answers",
            ) from error

        evaluated = {index: grade for (index, _), grade in zip(filled, grades)}

    results = []
    for index in range(len(payload.answers)):
        grade = evaluated.get(index)
        if grade is None:
            results.append(
                CheckedAnswer(index=index, score=0, feedback=EMPTY_ANSWER_FEEDBACK)
            )
        else:
            results.append(
                CheckedAnswer(index=index, score=grade.score, feedback=grade.feedback)
            )

    return QuizCheckResponse(results=results)
