# Tasks

## 1. Настройки и зависимости

- [x] 1.1 Добавить в `app/core/config.py` настройки GigaChat (`gigachat_credentials`, `gigachat_scope`, `gigachat_model="GigaChat-3-Ultra"`, `gigachat_timeout=120`, `gigachat_verify_ssl=False`) и `max_material_tokens=30000`; продублировать их в `backend/.env.example` с комментарием, что `GIGACHAT_VERIFY_SSL=true` требует `GIGACHAT_CA_BUNDLE_FILE`. Проверка: `uv run python -c "from app.core.config import settings; print(settings.gigachat_model, settings.max_material_tokens)"` печатает `GigaChat-3-Ultra 30000`.
- [x] 1.2 Зафиксировать зависимости `pdfplumber` и `langchain-gigachat` в `backend/pyproject.toml`. Проверка: `uv sync` завершается без ошибок, `uv run python -c "import pdfplumber, langchain_gigachat"` не падает.

## 2. Извлечение текста из PDF

- [x] 2.1 Создать `app/services/pdf.py` с извлечением текста через `pdfplumber` (постраничный `extract_text()` без `layout=True`) и локальной оценкой токенов `len(text) / 4.6`; определить исключения `EmptyPdfText` и `MaterialTooLarge`. Проверка: `uv run python -c` на файле `1706.03762v7.pdf` возвращает текст длиннее 30 000 символов (факт: 39 719) и оценку в диапазоне 8 500–8 800 токенов (факт: 8 635).
- [x] 2.2 Сузить `ALLOWED_EXTENSIONS` в `app/services/materials.py` до `{".pdf"}` и встроить извлечение в `create_material`: текст сохраняется в `extracted_text`, статус `ready`; при пустом тексте или превышении лимита файл удаляется и запись не создаётся. Проверка: загрузка `.docx` даёт `415`, PDF с пустым текстовым слоем и PDF сверх лимита дают `422`, после каждого отказа каталог `backend/storage/materials/` не содержит новой папки.

## 3. Схема ответа и клиент GigaChat

- [x] 3.1 Создать `app/schemas/quiz.py`: `Question` (`text`, `options`, `correct_index`) и `Quiz` (`summary`, `questions`). Проверка: `Quiz.model_validate` отклоняет пустой `questions` и `correct_index` вне диапазона `options` — проверено запуском на двух примерах данных.
- [x] 3.2 Создать `app/services/prompts/quiz.py` с промптом генерации: роль, требование опираться только на переданный текст, число вопросов и вариантов, запрет выходить за материал. Проверка: промпт лежит в отдельном модуле и не содержит текста материала; импорт модуля не тянет сервисы.
- [x] 3.3 Создать `app/services/gigachat.py`: ленивый синглтон клиента (`lru_cache`) из настроек и `generate_quiz(text)` через `with_structured_output(Quiz)` с ручной проверкой структуры ответа. Проверка: живой вызов на извлечённом тексте `1706.03762v7.pdf` возвращает `Quiz` с непустыми `summary` и `questions`; подмена ответа на невалидный (индекс вне диапазона) приводит к исключению, а не к возврату объекта.

## 4. API и уборка

- [x] 4.1 Добавить `POST /materials/{id}/quiz` в `app/api/routes/materials.py` с кодами `404` (чужой или неизвестный материал), `422` (нет извлечённого текста), `502` (ошибка модели или невалидная структура). Проверка: в `/docs` эндпоинт виден, без токена даёт `401`, с токеном на своём материале — `200`, на неизвестном идентификаторе — `404`.
- [x] 4.2 Обновить текст ошибки `415` на «Only .pdf files are supported» и согласовать с `accept` в `frontend/src/components/materials-block.tsx`. Проверка: загрузка `.docx` возвращает обновлённое сообщение, поле выбора файла предлагает только PDF.
- [x] 4.3 Удалить временный `backend/scripts/spike_gigachat.py` и убрать `1706.03762v7.pdf` из корня проекта (либо добавить в `.gitignore`, если файл нужен для ручных проверок). Проверка: `git status --short` не показывает скрипт замера и PDF.

## 5. Сквозная проверка

- [x] 5.1 Пройти сценарий целиком на чистой базе: регистрация → вход → загрузка `1706.03762v7.pdf` → `POST /materials/{id}/quiz`. Проверка: `201` при загрузке, `200` с непустыми `summary` и `questions` при генерации, в логе backend видно один запрос к GigaChat, в `studymate.db` у материала заполнен `extracted_text`.

## 6. Frontend

- [x] 6.1 Добавить в `frontend/src/lib/api.ts` типы `Quiz`/`QuizQuestion`, функцию `generateQuiz(materialId)` и обработку `502` в `describeError`. Проверка: `node node_modules/typescript/bin/tsc --noEmit` завершается с кодом 0.
- [x] 6.2 Создать `frontend/src/components/quiz-block.tsx`: выбор материала кнопками, генерация с блокировкой на время запроса, показ краткого содержания и вопросов с отмеченным верным вариантом, понятные ошибки, пустое состояние без материалов. Проверка: `node node_modules/eslint/bin/eslint.js src` не выдаёт замечаний по этому файлу.
- [x] 6.3 Заменить заглушку «Тесты» на `QuizBlock` в `frontend/src/app/page.tsx`, передав материалы из уже загруженного состояния. Проверка: `tsc --noEmit` и `eslint src` дают только две прежние ошибки `react-hooks/set-state-in-effect` в `page.tsx` и `use-session.ts`, новых не появляется.

## Workflow follow-up

- Заархивировать change после проверки всех задач и перенести дельты в `openspec/specs/`.
- Проверить, что спека `learning-materials` после архивации больше не упоминает `.docx` и `.pptx`.
- Проверить карточку «Тест» в браузере: backend и frontend запущены, материал выбран, тест пришёл и отрисовался.
