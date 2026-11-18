"""Проверка работоспособности сервиса."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", summary="Проверка работоспособности")
def read_health() -> dict[str, str]:
    """Отвечает без аутентификации, поэтому работает и на пустой базе."""
    return {"status": "ok"}
