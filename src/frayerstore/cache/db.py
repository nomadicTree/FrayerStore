"""Wrapper to cache DB connection"""

import streamlit as st
from frayerstore.core.db import get_db_uncached
from frayerstore.settings import load_settings
import sqlite3

settings = load_settings()


@st.cache_resource(ttl=settings.cache.db_connection_ttl)
def get_db() -> sqlite3.Connection:
    """Return a cached connection to the database"""
    conn = get_db_uncached()
    return conn
