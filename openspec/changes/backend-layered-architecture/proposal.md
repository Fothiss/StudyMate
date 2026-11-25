# Proposal

## Why

`app/services/` сейчас выполняет роль сразу трёх слоёв. `services/materials.py` в одном модуле держит работу с файлами (`store_file`, `sanitize_filename`), парсинг PDF, SQL-запросы (`select(Material)`) и управление транзакцией (`db.add` / `commit` / `rollback`), причём в `create_material` файл на диске и транзакция откатываются в одном `try` — границы файловой системы и БД переплетены. Доступа к данным как отдельного слоя нет, а зависимости собираются в `api/deps.py`, то есть HTTP-слой знает про все сервисы.

Следующий change добавляет шесть таблиц и десяток запросов. Если писать их в текущем стиле, объём перемешанного кода вырастет вдвое, а переписывать придётся уже больше. Поэтому слои разводятся **до** работы с БД, а не после.

## What Changes

- Новый файл `services/storage.py`: `sanitize_filename`, `material_directory`, `relative_file_path`, `store_file`, `remove_directory` переезжают из `services/materials.py`. Работа с диском перестаёт быть частью доменного сервиса.
- Новый пакет `repositories/`: `base.py` (общий конструктор с `Session`) и репозитории по доменам — `users.py`, `materials.py`. Репозиторий содержит только `select`/`flush` и **никогда не вызывает `commit`**.
- `services/users.py` и `services/materials.py` становятся классами (`AccountService`, `MaterialService`) с внедрёнными репозиториями. Границей транзакции владеет сервис: `commit` и `rollback` живут только здесь.
- Новый пакет `dependencies/` как единая точка сборки: `database.py` (`get_db`, `DbSession`), `security.py` (`oauth2_scheme`, `get_current_user`, `CurrentUser`), `repositories.py` (`get_*_repo` + алиасы), `services.py` (`get_*_service` + алиасы).
- `api/deps.py` удаляется; роутеры получают готовые зависимости через `Annotated`-алиасы вместо повторяющихся `db: Session = Depends(get_db)` в каждом эндпоинте.
- `AGENTS.md`: раздел `Architecture` дополняется `repositories/`, `dependencies/` и `services/storage.py`; уточняется, что локально по умолчанию используется SQLite, а PostgreSQL — целевая СУБД.
- **Поведение не меняется**: ни один код ответа, ни одно поле, ни одна валидация. Спеки проекта не изменяются.

Клиент GigaChat (`services/gigachat.py`) остаётся модулем функций: у него нет зависимостей от БД, поэтому в DI он не заводится — иначе появилась бы прокладка ради симметрии.

## Capabilities

### New Capabilities

Нет. Change не вводит и не меняет наблюдаемое поведение системы.

### Modified Capabilities

Нет. Это чистый рефакторинг: спеки описывают поведение, а оно остаётся прежним, поэтому `skip_specs: true` в `.openspec.yaml`.

## Impact

- Новые файлы: `app/services/storage.py`, `app/repositories/{__init__,base,users,materials}.py`, `app/dependencies/{__init__,database,security,repositories,services}.py`.
- Изменяемые файлы: `app/services/materials.py`, `app/services/users.py`, `app/api/routes/{auth,users,materials,quiz}.py`, `AGENTS.md`.
- Удаляемый файл: `app/api/deps.py`.
- API: без изменений — те же пути, коды и тела ответов.
- Зависимости: новых нет, DI строится на штатном `fastapi.Depends` и `app.dependency_overrides`.
- Вне scope: любые изменения схемы БД, новые эндпоинты, тесты (их вынесли отдельно), миграции Alembic, переход на PostgreSQL, `DOCX`/`PPTX`.
