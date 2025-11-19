import sqlite3
from src.frayerstore.paths import DB_PATH
from pathlib import Path


def open_db_at(path: Path) -> sqlite3.Connection:
    """Open a new connection to a database at given path"""
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def get_db_uncached() -> sqlite3.Connection:
    return open_db_at(DB_PATH)
