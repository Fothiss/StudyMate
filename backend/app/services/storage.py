"""Хранение файлов учебных материалов.

Модуль отвечает только за диск: как называется файл, куда он пишется и как
удаляется. Проверки, связанные с содержимым материала, живут в сервисе.
"""

import shutil
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings

MATERIALS_SUBDIR = "materials"
CHUNK_SIZE = 1024 * 1024
FALLBACK_NAME = "material"
MAX_FILENAME_LENGTH = 255


class UnsupportedFileType(Exception):
    """Файл не подходит: расширение вне белого списка или путь вне каталога."""


class FileTooLarge(Exception):
    """Файл превышает `max_upload_mb`."""


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
