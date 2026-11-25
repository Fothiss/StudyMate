"""Доступ к сохранённым тестам."""

from sqlalchemy import select

from app.models.test import Test
from app.repositories.base import BaseRepository


class TestRepository(BaseRepository):
    """Создание и чтение тестов пользователя."""

    def add(self, test: Test) -> Test:
        """Добавляет тест с вопросами и делает строки видимыми в транзакции."""
        self._session.add(test)
        self._session.flush()
        return test

    def get_owned(self, user_id: str, test_id: str) -> Test | None:
        """Тест по идентификатору, только если он принадлежит пользователю."""
        statement = select(Test).where(Test.id == test_id, Test.user_id == user_id)
        return self._session.scalar(statement)

    def list_for_material(self, material_id: str) -> list[Test]:
        """Тесты, сгенерированные по материалу, новые сверху."""
        statement = (
            select(Test)
            .where(Test.material_id == material_id)
            .order_by(Test.created_at.desc(), Test.id)
        )
        return list(self._session.scalars(statement))
