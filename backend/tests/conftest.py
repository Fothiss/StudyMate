"""Общие фикстуры тестов.

БД подменяется через `dependency_overrides` на `get_db`: временный файл SQLite
лежит в `tests/.tmp`, потому что `:memory:` из другого потока `TestClient` не
виден. Модель подменяется через `AIServiceDep`, поэтому тесты не ходят в сеть.
"""

import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app import models  # noqa: F401  импорт регистрирует таблицы в metadata
from app.core.config import settings
from app.core.db import Base
from app.dependencies.database import get_db
from app.dependencies.services import get_ai_service
from app.main import app
from tests.helpers import FakeAI, register_and_login, upload_material

TESTS_DIR = Path(__file__).resolve().parent
TMP_DIR = TESTS_DIR / ".tmp"


@pytest.fixture
def workdir() -> Iterator[Path]:
    """Каталог под файлы теста: системный temp песочницей закрыт."""
    shutil.rmtree(TMP_DIR, ignore_errors=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    try:
        yield TMP_DIR
    finally:
        shutil.rmtree(TMP_DIR, ignore_errors=True)


@pytest.fixture
def engine(workdir: Path) -> Iterator[Engine]:
    """Движок временной базы с созданной схемой."""
    db_url = f"sqlite:///{(workdir / 'test.db').as_posix()}"
    test_engine = create_engine(
        db_url, connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(test_engine)
    try:
        yield test_engine
    finally:
        test_engine.dispose()


@pytest.fixture
def session_factory(engine: Engine) -> sessionmaker[Session]:
    """Фабрика сессий той же базы, что видит приложение."""
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture
def session(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    """Сессия для проверок содержимого базы."""
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(
    session_factory: sessionmaker[Session],
    workdir: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[TestClient]:
    """Клиент приложения на временной базе и временном хранилище файлов."""
    monkeypatch.setattr(settings, "storage_dir", workdir / "storage")

    def override_get_db() -> Iterator[Session]:
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        # Без `with`: lifespan создал бы таблицы в боевой базе.
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def fake_ai() -> FakeAI:
    """Модель-заглушка по умолчанию."""
    return FakeAI()


@pytest.fixture
def api(client: TestClient, fake_ai: FakeAI) -> Iterator[TestClient]:
    """Клиент с подменённой моделью."""
    app.dependency_overrides[get_ai_service] = lambda: fake_ai
    try:
        yield client
    finally:
        app.dependency_overrides.pop(get_ai_service, None)


@pytest.fixture
def auth(api: TestClient) -> dict[str, str]:
    """Заголовок авторизации пользователя `student`."""
    return register_and_login(api, "student")


@pytest.fixture
def other_auth(api: TestClient) -> dict[str, str]:
    """Заголовок авторизации второго пользователя."""
    return register_and_login(api, "stranger")


@pytest.fixture
def material(api: TestClient, auth: dict[str, str]) -> dict[str, object]:
    """Материал пользователя `student`."""
    return upload_material(api, auth)
