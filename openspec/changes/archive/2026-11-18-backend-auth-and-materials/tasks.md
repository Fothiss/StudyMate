# Tasks

## 1. Фундамент и окружение

- [x] 1.1 Исправить `backend/pyproject.toml`: убрать `[build-system]` и `[project.scripts]`, добавить `[tool.uv] package = false`, заменить `description` и заполнить пустой `backend/README.md` одной строкой о проекте. Проверка: `cd backend; uv sync` завершается успешно и не пытается собрать пакет.
- [x] 1.2 Добавить зависимости командой `uv add fastapi "uvicorn[standard]" sqlalchemy pydantic-settings python-multipart pyjwt bcrypt`. Проверка: `uv sync` без ошибок, все семь пакетов видны в `uv pip list`.
- [x] 1.3 Дополнить `.gitignore` записями `*.db`, `backend/storage/`, `backend/.env`, `backend/.env.*` (кроме `.env.example`). Проверка: `git status` не показывает `studymate.db`, `storage/` и `.env` в неотслеживаемых.
- [x] 1.4 Создать `backend/.env.example` (`DATABASE_URL`, `SECRET_KEY`, `STORAGE_DIR`, `MAX_UPLOAD_MB=20`, `ACCESS_TOKEN_TTL_MINUTES=1440`, `CORS_ORIGINS`) и `app/core/config.py` на `pydantic-settings` с абсолютными путями от `Path(__file__).resolve().parents[1]`. Проверка: `uv run python -c "from app.core.config import settings; print(settings.database_url, settings.storage_dir)"` печатает абсолютный путь к `backend/studymate.db`.
- [x] 1.5 Создать `app/core/db.py` (`engine`, `SessionLocal`, `Base`, `get_db`) и `app/core/sqlite.py` с event-listener, выставляющим `PRAGMA foreign_keys=ON`. Проверка: `uv run python -c "from app.core.db import engine; print(engine.connect().exec_driver_sql('PRAGMA foreign_keys').scalar())"` печатает `1`.
- [x] 1.6 Создать `app/main.py` с `FastAPI`, CORS из настроек, `lifespan` (создание схемы) и роутером `app/api/routes/health.py` на `GET /health`. Проверка: `uv run uvicorn app.main:app --reload` стартует, `GET /health` отдаёт `200` и `{"status":"ok"}`, `http://127.0.0.1:8000/docs` открывается, файл `backend/studymate.db` создан.
- [x] 1.7 Записать в `README.md` раздел запуска backend через `uv` (`uv sync`, копирование `.env`, `uv run uvicorn`), без упоминания pip и `requirements.txt`. Проверка: команды из README выполняются дословно с нуля в новом терминале.

## 2. Аутентификация

- [x] 2.1 Создать `app/models/base.py` (миксин с `id: String(36)` и `created_at`) и `app/models/user.py` (`username` уникальный индекс, `password_hash`, `full_name`). Проверка: после старта приложения в `studymate.db` есть таблица `users` с уникальным индексом на `username`.
- [x] 2.2 Создать `app/core/security.py`: хеширование и проверка через `bcrypt`, выпуск и разбор JWT (HS256, срок жизни из настроек) на `pyjwt`. Проверка: `uv run python -c ...` — хеш не равен исходному паролю, `verify` возвращает `True`, `decode` возвращает исходный `sub`.
- [x] 2.3 Создать `app/schemas/user.py`: `Register` (ограничения `username` 3–64 и допустимые символы, пароль 8–72), `UserRead` (без `password_hash`), `Token`. Проверка: регистрация с паролем из 7 символов даёт `422`, с 73 символами — тоже `422`.
- [x] 2.4 Создать `app/services/users.py`: `create_user` (явная проверка дубликата плюс перехват `IntegrityError`) и `authenticate`. Проверка: повторная регистрация того же `username` даёт `409`, `authenticate` с неверным паролем возвращает `None`.
- [x] 2.5 Создать `app/api/deps.py` с `get_current_user` на `OAuth2PasswordBearer`. Проверка: запрос без заголовка `Authorization` даёт `401`, с действующим токеном возвращает пользователя из БД.
- [x] 2.6 Создать `app/api/routes/auth.py`: `POST /auth/register` и `POST /auth/login` на `OAuth2PasswordRequestForm`. Проверка: регистрация отдаёт `201` без поля с хешем, логин отдаёт `200` и `access_token` с `token_type: bearer`, неверный пароль и несуществующий `username` дают одинаковое тело `401`.
- [x] 2.7 Создать `app/api/routes/users.py` с `GET /users/me`. Проверка: с токеном `200` и поля `id`, `username`, `full_name`, `created_at`; без токена `401`.
- [x] 2.8 Проверить в `/docs` кнопку **Authorize**: вход через неё открывает доступ к `/users/me`. Проверка: передача чужого `user_id` в query-параметре не меняет пользователя, от имени которого выполняется запрос.

## 3. Материалы

- [x] 3.1 Создать `app/models/material.py`: `user_id` с внешним ключом на `users`, `title`, `filename`, `file_path`, `created_at`, а также пустые `extracted_text: TEXT NULL` и `extraction_status` как задел под извлечение текста. Проверка: таблица `materials` создаётся со внешним ключом на `users`, при удалении пользователя её строки удаляются (проверить `PRAGMA foreign_key_list(materials)`).
- [x] 3.2 Создать `app/schemas/material.py` с `MaterialRead` (`id`, `title`, `filename`, `created_at`) без внутреннего пути к файлу. Проверка: ответ API не содержит поля `file_path`.
- [x] 3.3 Создать `app/services/materials.py`: белый список расширений, лимит размера при потоковом копировании, санитайз имени файла, запись в `STORAGE_DIR/materials/{material_id}/{name}` и проверка, что итоговый путь лежит внутри каталога материала. Проверка: при превышении лимита не остаётся ни файла, ни записи; при имени `../evil.pdf` файл оказывается внутри каталога материала.
- [x] 3.4 Создать `app/api/routes/materials.py`: `POST /materials` (multipart `file` + `title`), `GET /materials`, `GET /materials/{id}`. Проверка: `201` для pdf/docx/pptx, `415` для `.txt`, `413` для файла сверх лимита, `422` при пустом `title`.
- [x] 3.5 Проверить изоляцию выдачи: пользователь B не видит материал пользователя A в `GET /materials` и получает `404` на `GET /materials/{id}` с идентификатором A. Проверка: ответы совпадают с ожидаемыми в сценариях спецификации `learning-materials`.
- [x] 3.6 Проверить коллизию имён и сохранение оригинального имени: два материала с одним `report.pdf` дают два разных файла на диске, а карточка каждого показывает исходное имя. Проверка: `Get-ChildItem backend/storage/materials -Recurse` показывает два файла в разных каталогах.
- [x] 3.7 Отметить в `docs/sql_scripts.sql` и `docs/er.md`, что источник истины — `backend/app/models/`, а схема упрощена до solo-варианта (без ролей, `assignments`/`results` → `attempts`). Проверка: пометка присутствует в обоих файлах.

## 4. Сквозная проверка

- [x] 4.1 Пройти полный сценарий в `/docs` на чистой базе: регистрация → вход → `GET /users/me` → загрузка `sample.pdf` → список → карточка. Проверка: все шаги возвращают коды из спецификаций, `backend/studymate.db` и файл в `backend/storage/materials/` существуют.
- [x] 4.2 Убедиться, что секреты не попали в репозиторий: `.env` не отслеживается git, `SECRET_KEY` не встречается в коде и в `.env.example` пуст. Проверка: `git status --short`, `Select-String -Path backend\app\*.py,backend\app\**\*.py -Pattern 'SECRET_KEY'` не находят захардкоженного значения.

## Workflow follow-up

- Заархивировать change после проверки всех задач и перенести дельты в `openspec/specs/`.
