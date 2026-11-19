"""Настройки приложения.

Значения читаются из переменных окружения и из `backend/.env`. Пути по умолчанию
строятся от каталога `backend/`, а не от текущего рабочего каталога: иначе запуск
`uv run` из корня проекта создал бы вторую базу данных.
"""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]

DEFAULT_DATABASE_URL = f"sqlite:///{(BACKEND_DIR / 'studymate.db').as_posix()}"


class Settings(BaseSettings):
    """Настройки backend, переопределяемые переменными окружения."""

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = DEFAULT_DATABASE_URL
    storage_dir: Path = BACKEND_DIR / "storage"
    secret_key: str = Field(min_length=16)
    access_token_ttl_minutes: int = 1440
    jwt_algorithm: str = "HS256"
    max_upload_mb: int = 20
    max_material_tokens: int = 30_000
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = True

    gigachat_credentials: str | None = None
    gigachat_scope: str = "GIGACHAT_API_PERS"
    gigachat_model: str = "GigaChat-3-Ultra"
    gigachat_timeout: float = 120.0
    # Локально окружение не доверяет цепочке GigaChat, поэтому проверка выключена.
    # Для продакшена нужен GIGACHAT_CA_BUNDLE_FILE с корневым сертификатом.
    gigachat_verify_ssl: bool = False

    @property
    def cors_origins_list(self) -> list[str]:
        """CORS-источники, разделённые запятой в переменной окружения."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def max_upload_bytes(self) -> int:
        """Лимит размера загружаемого файла в байтах."""
        return self.max_upload_mb * 1024 * 1024


settings = Settings()
