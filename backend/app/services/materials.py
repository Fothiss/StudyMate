"""Хранение файлов учебных материалов и запросы к ним."""

import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.material import Material
from app.models.user import User

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".pptx"}
MATERIALS_SUBDIR = "materials"
CHUNK_SIZE = 1024 * 1024
FALLBACK_NAME = "material"
MAX_FILENAME_LENGTH = 255


class UnsupportedFileType(Exception):
    """Расширение файла не входит в белый список."""


class FileTooLarge(Exception):
    """Файл превышает `MAX_UPLOAD_MB`."""


def sanitize_filename(raw: str) -> str:
    """Оставляет только имя файла.

    Разделители путей и `..` не должны попадать в имя: иначе клиент смог бы
    влиять на то, куда запишется файл.
    """
    name = raw.replace("\\", "/").split("/")[-1]
    name = name.replace("\x00", "").strip()
    if name in {"", ".", ".."}:
        name = FALLBACK_NAME
    return name[:MAX_FILENAME_LENGTH]


def material_directory(material_id: str) -> Path:
    """Каталог файлов конкретного материала."""
    return (settings.storage_dir / MATERIALS_SUBDIR / material_id).resolve()


def relative_file_path(material_id: str, filename: str) -> str:
    """Путь к файлу относительно каталога хранилища."""
    return f"{MATERIALS_SUBDIR}/{material_id}/{filename}"


def remove_directory(material_id: str) -> None:
    """Удаляет каталог материала, если запись создать не удалось."""
    shutil.rmtree(material_directory(material_id), ignore_errors=True)


def store_file(upload: UploadFile, material_id: str, filename: str) -> str:
    """Пишет файл в каталог материала и возвращает путь относительно хранилища.

    Размер проверяется по ходу копирования, поэтому файл не разрастается сверх
    лимита; недописанный файл удаляется.
    """
    directory = material_directory(material_id)
    directory.mkdir(parents=True, exist_ok=True)

    target = (directory / filename).resolve()
    if target.parent != directory:
        raise UnsupportedFileType

    limit = settings.max_upload_bytes
    written = 0
    try:
        with target.open("wb") as sink:
            while chunk := upload.file.read(CHUNK_SIZE):
                written += len(chunk)
                if written > limit:
                    raise FileTooLarge
                sink.write(chunk)
    except BaseException:
        target.unlink(missing_ok=True)
        raise

    return relative_file_path(material_id, filename)


def create_material(db: Session, *, user: User, title: str, upload: UploadFile) -> Material:
    """Сохраняет файл на диск и создаёт связанную с пользователем запись."""
    filename = sanitize_filename(upload.filename or "")
    if Path(filename).suffix.lower() not in ALLOWED_EXTENSIONS:
        raise UnsupportedFileType

    material_id = str(uuid4())
    try:
        stored_path = store_file(upload, material_id, filename)
    except (FileTooLarge, UnsupportedFileType):
        remove_directory(material_id)
        raise
    except OSError:
        remove_directory(material_id)
        raise

    material = Material(
        id=material_id,
        user_id=user.id,
        title=title,
        filename=filename,
        file_path=stored_path,
    )
    db.add(material)
    try:
        db.commit()
    except BaseException:
        db.rollback()
        remove_directory(material_id)
        raise
    db.refresh(material)
    return material


def list_materials(db: Session, user: User) -> list[Material]:
    """Материалы пользователя, новые сверху."""
    statement = (
        select(Material)
        .where(Material.user_id == user.id)
        .order_by(Material.created_at.desc())
    )
    return list(db.scalars(statement))


def get_material(db: Session, user: User, material_id: str) -> Material | None:
    """Материал пользователя по идентификатору; чужой материал неотличим от отсутствующего."""
    statement = select(Material).where(
        Material.id == material_id,
        Material.user_id == user.id,
    )
    return db.scalar(statement)
