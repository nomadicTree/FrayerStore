import sqlite3
from frayerstore.core.config import DB_PATH
from pathlib import Path


def open_connection(path: Path) -> sqlite3.Connection:
    """Open and configure a new SQLite connection."""
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")

    return conn


def get_connection() -> sqlite3.Connection:
    """Open the default DB as defined in config."""
    return open_connection(DB_PATH)
