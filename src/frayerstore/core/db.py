import sqlite3
from frayerstore.paths import DB_PATH


def get_db_uncached() -> sqlite3.Connection:
    """Open a new connection to the database"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
