"""Материалы: сохранение, извлечение текста и чтение."""

from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.models.material import Material
from app.models.user import User
from app.repositories.materials import MaterialRepository
from app.services import storage
from app.services.pdf import EmptyPdfText, MaterialTooLarge, extract_material_text
from app.services.storage import FileTooLarge, UnsupportedFileType

# Пока поддерживается только PDF: остальные форматы не парсятся.
ALLOWED_EXTENSIONS = {".pdf"}
EXTRACTION_READY = "ready"


class MaterialService:
    """Загрузка и чтение материалов пользователя.

    Сервис владеет границей транзакции и тем, что происходит с файлом при
    ошибке: репозиторий только готовит строку.
    """

    def __init__(self, materials: MaterialRepository) -> None:
        self._materials = materials

    def create(self, *, user: User, title: str, upload: UploadFile) -> Material:
        """Сохраняет файл на диск, извлекает текст и создаёт запись материала.

        Материал без текстового слоя или сверх лимита токенов не сохраняется:
        каталог файла удаляется, запись не создаётся.
        """
        filename = storage.sanitize_filename(upload.filename or "")
        if Path(filename).suffix.lower() not in ALLOWED_EXTENSIONS:
            raise UnsupportedFileType

        material_id = str(uuid4())
        try:
            stored_path = storage.store_file(upload, material_id, filename)
            text, _tokens = extract_material_text(
                storage.material_directory(material_id) / filename
            )
        except (FileTooLarge, UnsupportedFileType, EmptyPdfText, MaterialTooLarge, OSError):
            storage.remove_directory(material_id)
            raise

        material = Material(
            id=material_id,
            user_id=user.id,
            title=title,
            filename=filename,
            file_path=stored_path,
            extracted_text=text,
            extraction_status=EXTRACTION_READY,
        )
        try:
            self._materials.add(material)
            self._materials.session.commit()
        except BaseException:
            self._materials.session.rollback()
            storage.remove_directory(material_id)
            raise
        return material

    def list(self, user: User) -> list[Material]:
        """Материалы пользователя, новые сверху."""
        return self._materials.list_for_user(user.id)

    def get(self, user: User, material_id: str) -> Material | None:
        """Материал пользователя; чужой материал неотличим от отсутствующего."""
        return self._materials.get_owned(user.id, material_id)
