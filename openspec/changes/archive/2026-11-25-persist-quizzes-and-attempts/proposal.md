# Proposal

## Why

Сгенерированный тест, ответы студента и оценки после проверки нигде не сохраняются: `material-quiz` прямо требует «не персистентовать», а UI держит состояние в `sessionStorage`, поэтому тест исчезает при закрытии вкладки. Из-за этого нельзя показать прогресс, нельзя вернуться к результату позже и нельзя проверить тестовые вопросы на сервере — клиент сравнивает `correct_index` сам.

Схема БД, которая это закрывает, уже продумана (в упрощениях solo-сценария), но не реализована. Change добавляет её и переносит тесты, ответы и оценки в базу. Опорой служит слоистая архитектура из `backend-layered-architecture`: запросы живут в репозиториях, транзакции — в сервисах.

## What Changes

- Новые таблицы: `tests`, `questions`, `closed_question_options`, `open_question_rubrics`, `attempts`, `answers`. Переносимые типы (`VARCHAR(36)`, `JSON`, `DATETIME`, `NUMERIC`), создаются через `Base.metadata.create_all` — существующие `users` и `materials` не меняются, удалять базу не нужно.
- `tests.summary` — колонка `JSON` для краткого содержания: без неё оно теряется при перезагрузке, а UI его показывает.
- `POST /materials/{id}/quiz` дополнительно сохраняет тест с вопросами, вариантами и эталонами и возвращает `test_id`. Прежние поля `summary` и `questions` **остаются на месте**, поэтому текущий UI продолжает работать без правок.
- Новый `POST /tests/{test_id}/attempts`: сохраняет попытку и ответы, проверяет тестовые вопросы **на сервере по данным БД** и сразу возвращает результат. Обращения к модели нет, поэтому ответ мгновенный.
- Новый `POST /attempts/{attempt_id}/check`: проверяет открытые ответы через GigaChat, беря эталоны из `open_question_rubrics`, и сохраняет балл с комментарием в `answers`.
- Новые `GET /attempts` и `GET /attempts/{attempt_id}`: история попыток и разбор одной попытки.
- `POST /quiz/check` объявляется устаревшим, но продолжает работать до `web-results-and-progress`, пока UI его использует.
- Появляется точка подмены модели `services/ai.py` с провайдером в DI: без неё первые тесты не смогли бы проверять генерацию и оценку без обращения к GigaChat.

Единый `final_score` не вычисляется: в теле попытки хранятся `choice_correct`/`choice_total` и `llm_score` по каждому открытому ответу, а `final_score` остаётся пустой колонкой под будущую логику.

## Capabilities

### New Capabilities

- `quiz-attempts`: хранение тестов и попыток, оценка тестовых вопросов на сервере, проверка открытых ответов по эталонам из БД, история попыток с изоляцией по владельцу.

### Modified Capabilities

- `material-quiz`: генерация больше не транзитивна — тест сохраняется и возвращает идентификатор; требование `Transient Quiz` удаляется.

## Impact

- Новые файлы: `app/models/{test,question,attempt,answer}.py`, `app/repositories/{tests,attempts}.py`, `app/schemas/attempt.py`, `app/services/attempts.py`, `app/services/ai.py` (точка подмены модели), `app/services/quiz_storage.py` (конвертер `Quiz` → строки), `app/services/open_answers.py` (общий код проверки), `app/api/routes/attempts.py`, `tests/`.
- Изменяемые файлы: `app/models/__init__.py`, `app/schemas/quiz.py` (`TestRead`), `app/services/materials.py` (сохранение теста), `app/api/routes/materials.py`, `app/api/routes/quiz.py`, `app/dependencies/{repositories,services}.py`, `app/main.py`, `pyproject.toml` (тестовые зависимости и настройка `pytest`), `.gitignore`.
- API: `POST /materials/{id}/quiz` получает поле `test_id` (аддитивно); новые `POST /tests/{id}/attempts`, `POST /attempts/{id}/check`, `GET /attempts`, `GET /attempts/{id}`; `POST /quiz/check` устаревает, но не удаляется.
- Зависимости: добавляется `pytest` и `httpx` (для `TestClient`) — первых тестов в проекте.
- Вне scope: правки фронтенда, удаление `POST /quiz/check`, скрытие `correct_index`/`reference` из ответа при прохождении, `DOCX`/`PPTX`, `Alembic`, фоновая проверка ответов, единый итоговый балл.
