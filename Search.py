import streamlit as st
from app_lib.models import Word
from app_lib.repositories import search_words


def search_query(query):
    rows = search_words(query)
    words = []
    for i in range(len(rows)):
        words.append(Word(rows[i]))
    return words


def display_search_results(results, query):
    if len(results) > 0:
        for i in range(len(results)):
            word = results[i]
            with st.expander(
                f"{word.word} – {word.subject_name}", expanded=False
            ):
                word.display_frayer(
                    include_subject_info=True, show_topics=True
                )
    elif len(query) > 0:
        st.info("No results found.")


st.set_page_config(page_title="FrayerStore")
st.title("Search")

# --- Read query from URL ---
params = st.query_params
url_query = params.get("q", "")

# --- Text input for search ---
input_value = st.text_input("Search FrayerStore", value=url_query).strip()

# --- If input differs from URL, update URL and stop to rerun ---
if input_value != url_query:
    if len(input_value) > 0:
        st.query_params["q"] = input_value
    else:
        st.query_params.clear()
    st.stop()  # this triggers rerun with updated URL on next render

# --- Perform search if query exists ---
results = []
if len(url_query) > 0:
    results = search_query(url_query)

display_search_results(results, url_query)
