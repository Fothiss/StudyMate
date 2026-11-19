"""Извлечение текста из PDF и оценка его размера в токенах."""

from pathlib import Path

import pdfplumber

from app.core.config import settings

# Средняя длина токена GigaChat. Та же формула, что в `langchain_gigachat`
# при `use_api_for_tokens=False`, поэтому отдельный вызов `/tokens/count` не нужен.
CHARS_PER_TOKEN = 4.6

# Значение по умолчанию (3) склеивает слова там, где глифы стоят плотно:
# вместо «Provided proper attribution» выходит «Providedproperattribution».
# Единица сохраняет пробелы и не разрывает слова.
X_TOLERANCE = 1


class EmptyPdfText(Exception):
    """В PDF нет текстового слоя: обычно это скан."""


class MaterialTooLarge(Exception):
    """Текста больше `MAX_MATERIAL_TOKENS`."""


def estimate_tokens(text: str) -> int:
    """Оценивает число токенов локально, без обращения к API."""
    return round(len(text) / CHARS_PER_TOKEN)


def extract_material_text(path: Path) -> tuple[str, int]:
    """Извлекает текст PDF и проверяет, что материал пригоден для генерации.

    Возвращает текст и оценку его размера. На непригодном материале бросает
    `EmptyPdfText` или `MaterialTooLarge`.

    `layout=True` не используется: он добивает строки пробелами до сетки
    страницы и заметно раздувает число токенов.
    """
    with pdfplumber.open(path) as pdf:
        pages = [page.extract_text(x_tolerance=X_TOLERANCE) or "" for page in pdf.pages]

    text = "\n\n".join(page.strip() for page in pages if page.strip())
    if not text:
        raise EmptyPdfText

    tokens = estimate_tokens(text)
    if tokens > settings.max_material_tokens:
        raise MaterialTooLarge

    return text, tokens
