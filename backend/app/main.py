"""Точка входа FastAPI-приложения StudyMate."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import attempts, auth, health, materials, quiz, users
from app.core.config import settings
from app.core.db import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Создаёт схему БД и каталог хранилища при старте приложения."""
    init_db()
    yield


app = FastAPI(title="StudyMate API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(materials.router)
app.include_router(quiz.router)
app.include_router(attempts.tests_router)
app.include_router(attempts.attempts_router)


if __name__ == "__main__":
    # Запуск в разработке: uv run python -m app.main
    # Порт, хост и автоперезапуск берутся из настроек (HOST, PORT, RELOAD в .env).
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
