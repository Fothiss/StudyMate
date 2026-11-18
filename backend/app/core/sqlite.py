"""Настройка соединений SQLite.

Внешние ключи в SQLite выключены по умолчанию и настраиваются на каждое
соединение, поэтому прагма выставляется в listener, а не один раз при старте.
"""

import sqlite3

from sqlalchemy import event
from sqlalchemy.engine import Engine


@event.listens_for(Engine, "connect")
def enable_foreign_keys(dbapi_connection: object, _connection_record: object) -> None:
    """Включает `PRAGMA foreign_keys=ON` для всех соединений SQLite."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
