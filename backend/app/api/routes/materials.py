"""Загрузка и просмотр учебных материалов."""

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.core.config import settings
from app.dependencies.security import CurrentUser
from app.dependencies.services import MaterialServiceDep
from app.models.material import Material
from app.models.question import QUESTION_CHOICE, Question
from app.models.test import Test
from app.schemas.material import MaterialRead
from app.schemas.quiz import (
    ChoiceQuestionRead,
    OpenQuestionRead,
    QuizRequest,
    TestRead,
)
from app.services.gigachat import QuizGenerationError
from app.services.pdf import EmptyPdfText, MaterialTooLarge
from app.services.storage import FileTooLarge, UnsupportedFileType

router = APIRouter(prefix="/materials", tags=["materials"])


@router.post(
    "",
    response_model=MaterialRead,
    status_code=status.HTTP_201_CREATED,
    summary="Загрузить материал",
)
def upload_material(
    service: MaterialServiceDep,
    current_user: CurrentUser,
    title: str = Form(..., min_length=1, max_length=255),
    file: UploadFile = File(...),
) -> Material:
    """Принимает файл материала и привязывает его к текущему пользователю."""
    try:
        return service.create(user=current_user, title=title, upload=file)
    except UnsupportedFileType as error:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only .pdf files are supported",
        ) from error
    except FileTooLarge as error:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {settings.max_upload_mb} MB",
        ) from error
    except EmptyPdfText as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="PDF has no text layer. Scanned documents are not supported",
        ) from error
    except MaterialTooLarge as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Extracted text exceeds {settings.max_material_tokens} tokens",
        ) from error


@router.get("", response_model=list[MaterialRead], summary="Список материалов")
def list_materials(service: MaterialServiceDep, current_user: CurrentUser) -> list[Material]:
    """Отдаёт только материалы текущего пользователя."""
    return service.list(current_user)


@router.get("/{material_id}", response_model=MaterialRead, summary="Карточка материала")
def read_material(
    material_id: str,
    service: MaterialServiceDep,
    current_user: CurrentUser,
) -> Material:
    """Отдаёт материал, только если он принадлежит текущему пользователю."""
    material = service.get(current_user, material_id)
    if material is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found",
        )
    return material


@router.post(
    "/{material_id}/quiz",
    response_model=TestRead,
    summary="Сгенерировать тест по материалу",
)
def generate_material_quiz(
    material_id: str,
    payload: QuizRequest,
    service: MaterialServiceDep,
    current_user: CurrentUser,
) -> TestRead:
    """Генерирует тест по тексту материала и сохраняет его.

    Ответ собирается из сохранённого теста, поэтому содержит идентификаторы
    вопросов: по ним сдача идёт через `POST /tests/{test_id}/attempts`.
    """
    material = service.get(current_user, material_id)
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
        test, _quiz = service.generate_quiz(
            user=current_user,
            material=material,
            payload=payload,
        )
    except QuizGenerationError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to generate quiz",
        ) from error

    return _test_view(test)


def _test_view(test: Test) -> TestRead:
    """Ответ генерации: только идентификаторы, текст и оболочка вопросов."""
    return TestRead(
        test_id=test.id,
        summary=test.summary,
        questions=[_question_view(question) for question in test.questions],
    )


def _question_view(question: Question) -> ChoiceQuestionRead | OpenQuestionRead:
    """Вопрос сохранённого теста в том виде, в котором его получает клиент.

    Правильный индекс и эталон остаются в БД: до сдачи клиент не должен знать
    ответы, а разбор попытки читает их уже из сохранённой строки.
    """
    if question.type == QUESTION_CHOICE:
        return ChoiceQuestionRead(
            question_id=question.id,
            text=question.text,
            options=[option.text for option in question.options],
        )
    return OpenQuestionRead(question_id=question.id, text=question.text)
