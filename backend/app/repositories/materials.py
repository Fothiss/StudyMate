"""Доступ к учебным материалам."""

from sqlalchemy import select

from app.models.material import Material
from app.repositories.base import BaseRepository


class MaterialRepository(BaseRepository):
    """Чтение и создание материалов пользователя."""

    def list_for_user(self, user_id: str) -> list[Material]:
        """Материалы пользователя, новые сверху."""
        statement = (
            select(Material)
            .where(Material.user_id == user_id)
            .order_by(Material.created_at.desc())
        )
        return list(self._session.scalars(statement))

    def get_owned(self, user_id: str, material_id: str) -> Material | None:
        """Материал по идентификатору, только если он принадлежит пользователю."""
        statement = select(Material).where(
            Material.id == material_id,
            Material.user_id == user_id,
        )
        return self._session.scalar(statement)

    def add(self, material: Material) -> Material:
        """Добавляет материал и делает строку видимой в текущей транзакции."""
        self._session.add(material)
        self._session.flush()
        return material
