"""Wrapper to cache DB connection"""

import streamlit as st
from app.core.db import get_db_uncached


@st.cache_resource
def get_db():
    return get_db_uncached
