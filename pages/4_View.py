import streamlit as st
from app_lib.models import Word
from app_lib.repositories import get_word_by_id
from app_lib.utils import apply_styles

PAGE_TITLE = "View"
st.set_page_config(page_title=f"FrayerStore | {PAGE_TITLE}", page_icon="🔎")
apply_styles()
query_params = st.query_params
id_param = query_params.get("id")  # returns a string or None

if id_param is None:
    st.info("No id given in URL")
else:
    try:
        word_id = int(id_param)
    except ValueError:
        st.error("Invalid id in URL")
        st.stop()
    word_row = get_word_by_id(word_id)
    if word_row is None:
        st.error(f"No word found with id {word_id}")
        st.stop()
    word = Word(word_row)
    word.display_frayer(show_subject=True, show_topics=True)
