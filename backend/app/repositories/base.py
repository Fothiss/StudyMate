"""Общая часть репозиториев.

Репозиторий отвечает только за доступ к данным: читает и подготавливает строки,
но не завершает транзакцию. Границей транзакции владеет сервис, поэтому сессия
доступна ему через свойство `session`.
"""

from sqlalchemy.orm import Session


class BaseRepository:
    """Репозиторий, работающий в сессии текущего запроса."""

    def __init__(self, session: Session) -> None:
        self._session = session

    @property
    def session(self) -> Session:
        """Сессия для управления транзакцией; завершает её только сервис."""
        return self._session

    def flush(self) -> None:
        """Отправляет накопленные изменения в БД, не завершая транзакцию."""
        self._session.flush()
