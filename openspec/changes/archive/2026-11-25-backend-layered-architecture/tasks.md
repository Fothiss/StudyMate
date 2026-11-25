# Tasks

## 1. Файловое хранилище

- [x] 1.1 Создать `app/services/storage.py` и перенести туда `sanitize_filename`, `material_directory`, `relative_file_path`, `store_file`, `remove_directory` без изменения логики. Проверка: `python -c "from app.services import storage"` выполняется без ошибок.
- [x] 1.2 Убрать перенесённые функции из `app/services/materials.py` и обновить импорты в сервисе и роутерах. Проверка: загрузка PDF через `POST /materials` отвечает `201`, не-PDF — `415`.

## 2. Слой репозиториев

- [x] 2.1 Создать `app/repositories/base.py` с общим конструктором, принимающим `Session`. Проверка: `grep -r "commit" app/repositories/` не находит вызовов.
- [x] 2.2 Создать `app/repositories/users.py`: `get(user_id)`, `get_by_username(username)`, `add(user)` с `flush` без `commit`. Проверка: `POST /auth/register` отвечает `201`, повторный логин — `409`.
- [x] 2.3 Создать `app/repositories/materials.py`: `list_for_user(user_id)` с сортировкой новые-сверху, `get_owned(user_id, material_id)`, `add(material)`. Проверка: `GET /materials` возвращает тот же список в том же порядке, что и до правки.

## 3. Сервисы как классы

- [x] 3.1 Перевести `app/services/users.py` в класс `AccountService(repository)` с методами `register` и `authenticate`; `commit`/`rollback` остаются внутри. Проверка: `201` на регистрацию, `409` на дубль логина, `401` на неверный пароль.
- [x] 3.2 Перевести `app/services/materials.py` в класс `MaterialService(repository)`; файл на диске откатывается при ошибке БД, транзакция — при ошибке файла. Проверка: файл сверх лимита (`413`) и PDF без текстового слоя (`422`) не оставляют ни записи, ни каталога в `storage/materials/`.
- [x] 3.3 Проверить, что `commit` и `rollback` не вызываются вне `app/services/`. Проверка: `grep -rn "db.commit\|db.rollback" app/` находит только сервисы.

## 4. Точка сборки зависимостей

- [x] 4.1 Создать `app/dependencies/database.py` с `get_db` и алиасом `DbSession`; `SessionLocal` остаётся в `app/core/db.py`. Проверка: импорт модуля и открытие `/health` отвечает `200`.
- [x] 4.2 Создать `app/dependencies/security.py` с `oauth2_scheme`, `get_current_user` (через репозиторий пользователей) и алиасом `CurrentUser`. Проверка: `GET /users/me` с токеном отвечает `200`, без токена — `401`.
- [x] 4.3 Создать `app/dependencies/repositories.py` с провайдерами `get_user_repo`/`get_material_repo` и алиасами `UserRepo`/`MaterialRepo`. Проверка: провайдеры состоят из одной строки и не содержат условий.
- [x] 4.4 Создать `app/dependencies/services.py` с провайдерами `get_account_service`/`get_material_service` и алиасами с суффиксом `Dep`. Проверка: алиасы не затеняют имена классов в модулях роутеров.
- [x] 4.5 Оставить `app/dependencies/__init__.py` пустым (только docstring). Проверка: `python -c "import app.main"` выполняется без циклического импорта.

## 5. Роутеры

- [x] 5.1 Перевести `app/api/routes/auth.py` на `AccountServiceDep`. Проверка: регистрация и вход отвечают теми же кодами, что и до правки.
- [x] 5.2 Перевести `app/api/routes/users.py` на `CurrentUser`. Проверка: `/users/me` возвращает `username` и `created_at`.
- [x] 5.3 Перевести `app/api/routes/materials.py` на `MaterialServiceDep`. Проверка: все три эндпоинта материалов сохраняют коды `201`, `200`, `404`, `413`, `415`, `422`.
- [x] 5.4 Перевести `app/api/routes/quiz.py` на `MaterialServiceDep`, клиент GigaChat продолжает импортироваться напрямую. Проверка: `POST /quiz/check` с пустым ответом отвечает `200` и баллом `0`, без обращения к модели.
- [x] 5.5 Удалить `app/api/deps.py`. Проверка: `grep -rn "api.deps\|from app.api import deps" app/` ничего не находит, приложение стартует.

## 6. Документация

- [x] 6.1 Обновить `AGENTS.md`: в разделе `Architecture` добавить `repositories/`, `dependencies/` и `services/storage.py`, в `Tech Stack` уточнить, что локально по умолчанию SQLite, а PostgreSQL — целевая СУБД. Проверка: каждый каталог, названный в `AGENTS.md`, существует, и каждый каталог в `backend/app/` назван.

## 7. Интеграционная проверка

- [x] 7.1 Сравнить `GET /openapi.json` до и после рефакторинга: набор путей, параметров и кодов ответов должен совпасть. Проверка: JSON-диф пуст.
- [x] 7.2 Прогнать девять обращений (`/health`, `POST /auth/register`, `POST /auth/login`, `GET /users/me`, `POST /materials`, `GET /materials`, `GET /materials/{id}`, `POST /materials/{id}/quiz`, `POST /quiz/check`) и сверить коды с состоянием до change. Проверка: все коды совпадают, генерация и проверка по-прежнему отвечают `200`.

## Workflow follow-up

- Проверить change и заархивировать после ревью.
