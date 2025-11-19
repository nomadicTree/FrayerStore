import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent()  # app/
DB_PATH = BASE_DIR / "data" / "frayerstore.db"


def get_db_uncached() -> sqlite3.Connection:
    """Open a connection to the database

    Returns:
        A connection object to the application's SQLite database.
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
