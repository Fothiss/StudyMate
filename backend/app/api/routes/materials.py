"""Загрузка и просмотр учебных материалов."""

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.db import get_db
from app.models.material import Material
from app.models.user import User
from app.schemas.material import MaterialRead
from app.schemas.quiz import Quiz, QuizRequest
from app.services import gigachat as gigachat_service
from app.services import materials as materials_service
from app.services.gigachat import QuizGenerationError
from app.services.materials import FileTooLarge, UnsupportedFileType
from app.services.pdf import EmptyPdfText, MaterialTooLarge

router = APIRouter(prefix="/materials", tags=["materials"])


@router.post(
    "",
    response_model=MaterialRead,
    status_code=status.HTTP_201_CREATED,
    summary="Загрузить материал",
)
def upload_material(
    title: str = Form(..., min_length=1, max_length=255),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Material:
    """Принимает файл материала и привязывает его к текущему пользователю."""
    try:
        return materials_service.create_material(
            db,
            user=current_user,
            title=title,
            upload=file,
        )
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
def list_materials(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Material]:
    """Отдаёт только материалы текущего пользователя."""
    return materials_service.list_materials(db, current_user)


@router.get("/{material_id}", response_model=MaterialRead, summary="Карточка материала")
def read_material(
    material_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Material:
    """Отдаёт материал, только если он принадлежит текущему пользователю."""
    material = materials_service.get_material(db, current_user, material_id)
    if material is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found",
        )
    return material


@router.post(
    "/{material_id}/quiz",
    response_model=Quiz,
    summary="Сгенерировать тест по материалу",
)
def generate_material_quiz(
    material_id: str,
    payload: QuizRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Quiz:
    """Генерирует вопросы по уже извлечённому тексту материала."""
    material = materials_service.get_material(db, current_user, material_id)
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
        return gigachat_service.generate_quiz(
            material.extracted_text,
            choice_count=payload.choice_count,
            open_count=payload.open_count,
        )
    except QuizGenerationError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to generate quiz",
        ) from error
