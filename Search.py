import streamlit as st
from app_lib.models import Word
from app_lib.repositories import search_words


def search_query(query):
    word_rows = search_words(query)
    words = []
    for r in word_rows:
        words.append(Word(r))
    return words


def display_search_results(results, query):
    if results:
        for word in results:
            with st.expander(
                f"{word.word} – {word.subject_name}", expanded=False
            ):
                word.display_frayer(
                    include_subject_info=True, show_topics=True
                )
    elif query:
        st.info("No results found.")


st.set_page_config(page_title="Frayer Store")
st.title("Search")

# Read current query safely from URL
query = st.query_params.get("q", [""])[0]

# Text input bound to local variable
input_query = st.text_input(
    "Search for a word", value=query, key="search_input"
).strip()

# Update URL if input differs from URL
if input_query != query:
    st.query_params = {"q": [input_query]}  # triggers rerun

# Run search using query from URL (after rerun)
search_term = st.query_params.get("q", [""])[0]
if search_term:
    results = search_query(search_term)
    display_search_results(results, search_term)
