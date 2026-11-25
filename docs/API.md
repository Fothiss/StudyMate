# API StudyMate

Контракт REST API между `frontend/` и `backend/`. Источник правды — код
`backend/app/api/routes/` и схемы `backend/app/schemas/`; при расхождении верен код.
Живая документация с возможностью отправки запросов — `http://127.0.0.1:8000/docs`
(Swagger UI, кнопка **Authorize** берёт токен из `POST /auth/login`).

**Статусы в этом документе:**

| Метка | Значение |
|---|---|
| `Реализован` | маршрут есть в приложении и отвечает по контракту ниже |
| `Не реализован` | маршрута в приложении нет |

## Общие правила

- **Базовый URL:** `http://127.0.0.1:8000` (настройка `HOST`/`PORT` в `backend/.env`).
- **Формат:** JSON, кроме `POST /auth/login` (форма) и `POST /materials` (multipart).
- **Аутентификация:** `Authorization: Bearer <access_token>`. Токен — JWT `HS256`,
  живёт `ACCESS_TOKEN_TTL_MINUTES` (по умолчанию 1440 минут = 24 часа); в `sub`
  лежит идентификатор пользователя. Без токена или с испорченным/просроченным
  токеном — `401`.
- **Изоляция данных:** пользователь определяется только по токену. Ни тело, ни
  query-параметры на выбор пользователя не влияют; чужой объект неотличим от
  несуществующего и даёт `404`.
- **Время:** ISO-8601 в UTC **без смещения** (`2026-11-25T10:25:09.023456`).
  Клиент обязан проставить зону сам, иначе браузер прочитает время как локальное.
- **Ошибки:** `HTTPException` отдаёт `{"detail": "<текст>"}`; ошибка валидации
  FastAPI — `422` с `{"detail": [{"type", "loc", "msg", "input"}]}`, клиент берёт
  `detail[0].msg`. Текст `detail` английский и не предназначен для показа
  пользователю: frontend переводит коды в русские сообщения сам.
- **Лимиты (настройки):** файл — `MAX_UPLOAD_MB` (20 МБ), текст материала —
  `MAX_MATERIAL_TOKENS` (30 000), вопросов за раз — до 15 тестовых и до 10 открытых.
- **CORS:** источники из `CORS_ORIGINS` (по умолчанию `http://localhost:3000` и
  `http://127.0.0.1:3000`).

## Сводка эндпоинтов

| Метод | Путь | Доступ | Назначение | Статус |
|---|---|---|---|---|
| `GET` | `/health` | публичный | Проверка работоспособности | Реализован |
| `POST` | `/auth/register` | публичный | Регистрация | Реализован |
| `POST` | `/auth/login` | публичный | Вход, выдача токена | Реализован |
| `GET` | `/users/me` | токен | Текущий пользователь | Реализован |
| `POST` | `/materials` | токен | Загрузка материала (PDF) | Реализован |
| `GET` | `/materials` | токен | Список материалов | Реализован |
| `GET` | `/materials/{material_id}` | токен | Карточка материала | Реализован |
| `POST` | `/materials/{material_id}/quiz` | токен | Генерация теста по материалу | Реализован |
| `POST` | `/tests/{test_id}/attempts` | токен | Сдача теста | Реализован |
| `POST` | `/attempts/{attempt_id}/check` | токен | Проверка открытых ответов | Реализован |
| `GET` | `/attempts` | токен | История попыток | Реализован |
| `GET` | `/attempts/{attempt_id}` | токен | Разбор попытки | Реализован |
| `POST` | `/quiz/check` | токен | Проверка открытых ответов по материалу | Не реализован (удалён) |

---

## GET /health

Проверка живости сервиса. Не требует токена, работает и на пустой базе.

**Ответ `200`**

```json
{ "status": "ok" }
```

---

## POST /auth/register

Создаёт учётную запись.

**Запрос** (`application/json`)

| Поле | Тип | Ограничения |
|---|---|---|
| `username` | string | 3–64 символа, `^[A-Za-z0-9_.-]+$` |
| `password` | string | 8–72 символа (ограничение bcrypt — 72 байта) |

```json
{ "username": "student", "password": "secret123" }
```

**Ответ `201`** — [`UserRead`](#userread)

```json
{ "id": "ef1f...", "username": "student", "created_at": "2026-11-25T10:25:09.023456" }
```

**Ошибки:** `409` — логин занят (`Username is already taken`); `422` — не прошли
ограничения полей.

---

## POST /auth/login

Выдаёт токен доступа. Тело — **форма** (`application/x-www-form-urlencoded`), как
требует OAuth2 password flow.

**Запрос**

| Поле | Тип | Описание |
|---|---|---|
| `username` | string | Логин |
| `password` | string | Пароль |

**Ответ `200`** — [`Token`](#token)

```json
{ "access_token": "eyJhbGciOi...", "token_type": "bearer" }
```

**Ошибки:** `401` — неверный логин **или** пароль (ответ одинаковый, чтобы нельзя
было перебором выяснить существующие учётки), заголовок `WWW-Authenticate: Bearer`;
`422` — не переданы поля формы.

---

## GET /users/me

Пользователь, определённый по токену.

**Ответ `200`** — [`UserRead`](#userread)

**Ошибки:** `401` — токена нет, подпись неверна, срок истёк или пользователь удалён.

---

## POST /materials

Загружает файл материала и извлекает из него текст. Поддерживается **только PDF**
с текстовым слоем (DOCX и PPTX не поддерживаются).

**Запрос** (`multipart/form-data`)

| Поле | Тип | Ограничения |
|---|---|---|
| `title` | string | 1–255 символов |
| `file` | файл | расширение `.pdf`, до `MAX_UPLOAD_MB` (20 МБ) |

**Ответ `201`** — [`MaterialRead`](#materialread)

**Ошибки:**

| Код | `detail` | Причина |
|---|---|---|
| `415` | `Only .pdf files are supported` | расширение не `.pdf` |
| `413` | `File exceeds 20 MB` | файл больше лимита |
| `422` | `PDF has no text layer...` | скан без текстового слоя |
| `422` | `Extracted text exceeds 30000 tokens` | текст длиннее лимита |
| `401` | `Could not validate credentials` | нет/невалидный токен |

---

## GET /materials

Материалы текущего пользователя, **новые сверху**.

**Ответ `200`** — массив [`MaterialRead`](#materialread); пустой массив, если
материалов нет.

---

## GET /materials/{material_id}

Карточка одного материала.

**Ответ `200`** — [`MaterialRead`](#materialread)

**Ошибки:** `404` — материала нет или он принадлежит другому пользователю.

---

## POST /materials/{material_id}/quiz

Генерирует тест по извлечённому тексту материала и **сохраняет** его. Может
занять до минуты: отвечает GigaChat. Правильные ответы и эталоны в ответ **не
попадают** — они остаются в БД до сдачи.

**Запрос** (`application/json`) — [`QuizRequest`](#quizrequest)

| Поле | Тип | По умолчанию | Ограничения |
|---|---|---|---|
| `choice_count` | int | 5 | 0–15 |
| `open_count` | int | 0 | 0–10 |

Сумма должна быть больше нуля.

**Ответ `200`** — [`TestRead`](#testread)

```json
{
  "test_id": "8c1d...",
  "summary": ["Фотосинтез превращает свет в химическую энергию"],
  "questions": [
    {
      "question_id": "0f2a...",
      "kind": "choice",
      "text": "Что запасает энергию?",
      "options": ["Глюкоза", "Кислород", "Вода"]
    },
    { "question_id": "77b1...", "kind": "open", "text": "Что такое фотосинтез?" }
  ]
}
```

**Ошибки:**

| Код | `detail` | Причина |
|---|---|---|
| `404` | `Material not found` | материала нет или он чужой |
| `422` | `Material has no extracted text` | у материала нет текста |
| `422` | ошибка валидации | оба счётчика нулевые или вне диапазона |
| `502` | `Failed to generate quiz` | модель недоступна или вернула невалидный ответ; тест не сохраняется |
| `401` | `Could not validate credentials` | нет/невалидный токен |

**Повторный вызов** создаёт новый тест с новым `test_id`; предыдущий не меняется.

---

## POST /tests/{test_id}/attempts

Сдаёт сохранённый тест: создаёт попытку и **сразу** оценивает тестовые вопросы по
вариантам из БД. Модель не вызывается, ответ приходит без ожидания.

**Запрос** (`application/json`) — [`AttemptSubmitRequest`](#attemptsubmitrequest)

```json
{
  "answers": [
    { "question_id": "0f2a...", "selected_index": 0 },
    { "question_id": "77b1...", "answer_text": "Свет превращается в химическую энергию" }
  ]
}
```

| Поле | Тип | Описание |
|---|---|---|
| `answers` | array | Может быть пустым: попытка всё равно создаётся |
| `answers[].question_id` | string | Вопрос теста |
| `answers[].selected_index` | int \| null | Позиция варианта в `options` (с 0). Вне диапазона — считается пропуском |
| `answers[].answer_text` | string \| null | Текст ответа на открытый вопрос; пробелы обрезаются |

Сервер не читает присланные `correct_index`, `reference` или идентификаторы
вариантов — верность берётся из БД. На каждый вопрос теста пишется ровно одна
строка ответа; неотвеченный сохраняется как пропуск, тестовый вопрос при этом
считается неверным.

**Ответ `201`** — `AttemptSubmitResponse`

```json
{
  "attempt_id": "a31c...",
  "status": "submitted",
  "choice_correct": 1,
  "choice_total": 1,
  "answers": [
    { "question_id": "0f2a...", "is_correct": true, "llm_score": null, "llm_feedback": null },
    { "question_id": "77b1...", "is_correct": null, "llm_score": null, "llm_feedback": null }
  ]
}
```

`status` — `submitted` (открытые ещё не проверены) или `checked`.

**Ошибки:** `404` — теста нет или он чужой (`Test not found`); `422` — ошибка
валидации тела; `401` — нет/невалидный токен.

---

## POST /attempts/{attempt_id}/check

Проверяет **сохранённые** открытые ответы попытки по эталонам из БД. Может занять
до 120 секунд (таймаут GigaChat). Повторный вызов перепроверяет и **перезаписывает**
оценки. Пустые ответы в модель не отправляются и получают `0` с пояснением.

**Запрос:** без тела.

**Ответ `200`** — `AttemptCheckResponse`

```json
{
  "attempt_id": "a31c...",
  "status": "checked",
  "answers": [
    { "question_id": "77b1...", "score": 80.0, "feedback": "Смысл передан верно" }
  ]
}
```

`score` — 0–100.

**Ошибки:**

| Код | `detail` | Причина |
|---|---|---|
| `404` | `Attempt not found` | попытки нет или она чужая |
| `502` | `Failed to evaluate answers` | модель недоступна или вернула невалидную оценку; оценки в БД не меняются |
| `401` | `Could not validate credentials` | нет/невалидный токен |

---

## GET /attempts

История попыток текущего пользователя, **новые сверху**. Пагинации нет: отдаётся
весь список.

**Ответ `200`** — массив [`AttemptSummaryRead`](#attemptsummaryread)

```json
[
  {
    "id": "a31c...",
    "test_id": "8c1d...",
    "material_id": "b7e4...",
    "material_title": "Конспект",
    "status": "checked",
    "choice_correct": 1,
    "choice_total": 1,
    "created_at": "2026-11-25T10:25:09.023456",
    "checked_at": "2026-11-25T10:26:11.001234"
  }
]
```

`choice_total = 0` означает, что в тесте не было тестовых вопросов, — это не «0 из 0».

---

## GET /attempts/{attempt_id}

Разбор попытки: вопросы теста, данные ответы, правильные варианты, эталоны и
сохранённые оценки. Правильные ответы здесь **есть** — это допустимо только для
уже сохранённой попытки.

**Ответ `200`** — [`AttemptDetailRead`](#attemptdetailread)

```json
{
  "id": "a31c...",
  "test_id": "8c1d...",
  "material_id": "b7e4...",
  "material_title": "Конспект",
  "status": "checked",
  "choice_correct": 1,
  "choice_total": 1,
  "created_at": "2026-11-25T10:25:09.023456",
  "checked_at": "2026-11-25T10:26:11.001234",
  "summary": ["Фотосинтез превращает свет в химическую энергию"],
  "questions": [
    {
      "question_id": "0f2a...",
      "type": "choice",
      "text": "Что запасает энергию?",
      "options": ["Глюкоза", "Кислород", "Вода"],
      "correct_index": 0,
      "selected_index": 1,
      "answer_text": null,
      "reference": null,
      "is_correct": false,
      "llm_score": null,
      "llm_feedback": null
    },
    {
      "question_id": "77b1...",
      "type": "open",
      "text": "Что такое фотосинтез?",
      "options": [],
      "correct_index": null,
      "selected_index": null,
      "answer_text": "Фотосинтез",
      "reference": "Процесс превращения световой энергии в химическую",
      "is_correct": null,
      "llm_score": 80.0,
      "llm_feedback": "Смысл передан верно"
    }
  ]
}
```

`null` в разборе значит: не отвечен (`selected_index`, `answer_text`), не проверялся
(`llm_score`, `llm_feedback`), не применимо к типу вопроса (`correct_index`,
`reference` у тестового, `is_correct` у открытого).

**Ошибки:** `404` — попытки нет или она чужая; `401` — нет/невалидный токен.

---

## Не реализовано

| Что | Статус | Почему / что вместо этого |
|---|---|---|
| `POST /quiz/check` — проверка открытых ответов по материалу | Не реализован (удалён) | Маршрут доверял эталону из тела запроса: клиент мог подставить выгодный ответ. Заменён на `POST /attempts/{attempt_id}/check`, где эталон читается из БД. Запрос на старый путь получает `404` |
| Загрузка DOCX и PPTX | Не реализовано | `ALLOWED_EXTENSIONS = {".pdf"}`; прочие расширения получают `415`. Форматы заявлены в README как цель, но не поддержаны |
| Чтение теста без сдачи (`GET /tests/{id}`) | Не реализовано | Черновик прохождения хранит вопросы на клиенте (`sessionStorage`), поэтому до сдачи тест повторно не запрашивается |
| Удаление материала или попытки | Не реализовано | Вне scope текущей версии: удаление повлекло бы каскад по тестам и ответам |
| Пагинация и фильтры истории (`limit`, `offset`) | Не реализовано | `GET /attempts` отдаёт весь список; при росте истории это станет отдельной задачей |
| Экспорт результатов | Не реализовано | Вне scope |
| Единый итоговый балл по попытке | Не реализовано | Шкалы «верно из N» и «0–100» несводимы; `attempts.final_score` в БД остаётся пустым |
| Статус извлечения текста в `MaterialRead` | Не реализовано | `extraction_status` хранится в БД, но наружу не отдаётся: материал без текста отклоняется ещё при загрузке |

---

## Схемы запросов и ответов

### UserRead

| Поле | Тип | Описание |
|---|---|---|
| `id` | string | Идентификатор пользователя |
| `username` | string | Логин |
| `created_at` | datetime | Создание учётной записи |

### Token

| Поле | Тип | Описание |
|---|---|---|
| `access_token` | string | JWT для заголовка `Authorization` |
| `token_type` | string | Всегда `bearer` |

### MaterialRead

| Поле | Тип | Описание |
|---|---|---|
| `id` | string | Идентификатор материала |
| `title` | string | Название, заданное при загрузке |
| `filename` | string | Исходное имя файла |
| `created_at` | datetime | Загрузка |

Путь к файлу на диске наружу не отдаётся.

### QuizRequest

| Поле | Тип | По умолчанию | Описание |
|---|---|---|---|
| `choice_count` | int | 5 | Тестовых вопросов, 0–15 |
| `open_count` | int | 0 | Открытых вопросов, 0–10 |

### TestRead

| Поле | Тип | Описание |
|---|---|---|
| `test_id` | string | Идентификатор сохранённого теста; нужен для сдачи |
| `summary` | string[] | Краткое содержание материала, непустой |
| `questions` | QuestionRead[] | Вопросы в порядке прохождения, непустой |

`QuestionRead` — размеченный по `kind` союз:

- `kind: "choice"` — `question_id`, `text`, `options` (от 2 вариантов);
- `kind: "open"` — `question_id`, `text`.

Правильных вариантов и эталонов в этой схеме нет.

### AttemptSubmitRequest

| Поле | Тип | Описание |
|---|---|---|
| `answers` | AttemptAnswerInput[] | Ответы; пустой список допустим |
| `answers[].question_id` | string | Вопрос теста |
| `answers[].selected_index` | int \| null | Позиция выбранного варианта |
| `answers[].answer_text` | string \| null | Текст ответа на открытый вопрос |

### AttemptSummaryRead

| Поле | Тип | Описание |
|---|---|---|
| `id` | string | Идентификатор попытки |
| `test_id` | string | Тест, по которому сдавалась |
| `material_id` | string | Материал теста |
| `material_title` | string | Название материала |
| `status` | string | `submitted` \| `checked` |
| `choice_correct` | int | Верных тестовых ответов |
| `choice_total` | int | Всего тестовых вопросов (0 — их не было) |
| `created_at` | datetime | Время сдачи |
| `checked_at` | datetime \| null | Время последней проверки открытых |

### AttemptDetailRead

Все поля `AttemptSummaryRead`, плюс:

| Поле | Тип | Описание |
|---|---|---|
| `summary` | string[] | Краткое содержание теста |
| `questions` | AttemptQuestionRead[] | По строке на каждый вопрос теста, в его порядке |

`AttemptQuestionRead`:

| Поле | Тип | Описание |
|---|---|---|
| `question_id` | string | Идентификатор вопроса |
| `type` | string | `choice` \| `open` |
| `text` | string | Формулировка |
| `options` | string[] | Варианты; у открытого — пустой список |
| `correct_index` | int \| null | Правильный вариант; у открытого `null` |
| `selected_index` | int \| null | Выбор пользователя; `null` — не отвечен |
| `answer_text` | string \| null | Текст открытого ответа |
| `reference` | string \| null | Эталон открытого вопроса; у тестового `null` |
| `is_correct` | bool \| null | Верность тестового ответа |
| `llm_score` | float \| null | Балл 0–100 за открытый ответ |
| `llm_feedback` | string \| null | Комментарий проверки |

---

## Как проверить контракт

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q      # контракт закреплён тестами
.\.venv\Scripts\python.exe -m pytest tests/test_openapi.py -q
```

`tests/test_openapi.py` проверяет наличие маршрутов и отсутствие удалённого
`/quiz/check`; `tests/test_quiz_generation.py` — что ответ генерации не содержит
`correct_index` и `reference`.

Покрытие маршрутов тестами: `test_health.py` — `/health`; `test_auth_materials.py` —
`/auth/*` и `/materials`; `test_quiz_generation.py` — `/materials/{id}/quiz`;
`test_attempts.py` и `test_full_scenario.py` — `/tests/{id}/attempts` и `/attempts`.
Единственный маршрут без своего теста — `GET /users/me`: он проверяется косвенно,
через экраны, которые без него не отрисуются.
