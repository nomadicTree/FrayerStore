import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]  # frayerstore/
DB_PATH = PROJECT_ROOT / "data" / "frayerstore.db"


def get_db_uncached() -> sqlite3.Connection:
    """Open a new connection to the database"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
