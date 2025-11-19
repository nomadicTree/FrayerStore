"""Wrapper to cache DB connection"""

import streamlit as st
from app.core.db import get_db_uncached
from app.settings import load_settings

settings = load_settings()


@st.cache_resource(ttl=settings.cache.db_connection_ttl)
def get_db():
    return get_db_uncached
