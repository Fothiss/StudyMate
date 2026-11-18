# Proposal

## Why

От StudyMate сейчас есть только `README.md` и схема БД в `docs/` — кода backend не существует. Без каркаса приложения, аутентификации и хранения учебных материалов ни одну следующую возможность (извлечение текста, генерация вопросов через GigaChat, прохождение тестов, статистика) начать нельзя: у них нет ни владельца данных, ни самих данных.

Этот change создаёт первый работающий вертикальный срез «зарегистрировался → загрузил материал → увидел только своё».

## What Changes

- Каркас FastAPI-приложения в `backend/app/`: настройки из `.env`, подключение к SQLite, создание схемы при старте.
- Регистрация и вход по `username`/`password` с выдачей JWT; эндпоинт текущего пользователя.
- Загрузка учебных материалов (PDF, DOCX, PPTX) в локальное хранилище, метаданные в БД, список и карточка только своих материалов.
- Исправление `backend/pyproject.toml`: проект объявляется несобираемым (`package = false`), удаляются `build-system` и `project.scripts`, указывающие на несуществующий модуль `backend`.
- Приведение схемы данных к solo-сценарию: без ролей, `assignments` и `results` объединяются в `attempts`. **BREAKING** по отношению к `docs/sql_scripts.sql`, но затрагивает только ещё не созданные таблицы, миграция существующих данных не требуется.

## Capabilities

### New Capabilities

- `user-auth`: регистрация, вход, выпуск и проверка JWT, определение текущего пользователя для защищённых запросов.
- `learning-materials`: приём файла учебного материала во внутреннее хранилище, хранение метаданных, выдача списка и карточки материалов, принадлежащих текущему пользователю.
- `service-health`: публичная проверка работоспособности сервиса без аутентификации.

### Modified Capabilities

Нет — в проекте ещё нет ни одной существующей спецификации.

## Impact

- Новый код: `backend/app/**` (`api/`, `core/`, `models/`, `schemas/`, `services/`, `main.py`), `backend/.env.example`.
- Изменяемые файлы: `backend/pyproject.toml`, `.gitignore`.
- Схема БД: создаётся с нуля в `backend/studymate.db` через `create_all`, без Alembic.
- Новые зависимости: `fastapi`, `uvicorn[standard]`, `sqlalchemy`, `pydantic-settings`, `python-multipart`, `pyjwt`, `bcrypt`.
- Новые эндпоинты: `GET /health`, `POST /auth/register`, `POST /auth/login`, `GET /users/me`, `POST /materials`, `GET /materials`, `GET /materials/{id}`.
- Файловое хранилище: `backend/storage/materials/{material_id}/{filename}`.
- Вне scope: извлечение текста из документов, GigaChat, генерация вопросов, прохождение тестов, статистика, frontend, миграции Alembic, роли и админка.
