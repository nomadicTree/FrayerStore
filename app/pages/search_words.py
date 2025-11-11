"""Streamlit page for searching the words database"""

import time
import streamlit as st
from app.core.respositories.words_repo import search_words
from app.core.utils.strings import format_time_text
from app.components.common import page_header
from app.core.models.word_models import SearchResult

# from app_lib.utils import apply_styles, render_frayer, format_time_text


PAGE_TITLE = "Search"


@st.cache_data(show_spinner=False)
def search_query(query: str):
    """Return matching words and search duration."""
    start_time = time.perf_counter()
    results = search_words(query)
    elapsed = time.perf_counter() - start_time
    return results, elapsed


def display_search_results(
    results: list[SearchResult], query: str, elapsed: float
):
    if not query:
        return

    plural = "s" if len(results) != 1 else ""
    st.caption(
        f"Found {len(results)} result{plural} for {query!r} in {format_time_text(elapsed)}."
    )

    if not results:
        st.info(f"No results found for {query!r}.")
        return

    for r in results:
        with st.container(border=True):
            st.markdown(f"#### [{r.word}]({r.url})")
            st.markdown(f"**{r.subject_name}**: {r.level_names or '—'}")


def main():
    """Page contents including search bar and search results"""
    page_header()

    # Initialize session state for search
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""
    if "search_results" not in st.session_state:
        st.session_state.search_results = []
    if "elapsed_time" not in st.session_state:
        st.session_state.elapsed_time = None

    # Search input
    query = st.text_input(
        "Search FrayerStore",
        value=st.session_state.search_query,
        key="search_input",
    )
    st.divider()

    with st.spinner("Searching..."):

        # Perform search only if the query changed
        if query.strip() and query != st.session_state.search_query:
            st.session_state.search_query = query
            if query:
                (
                    st.session_state.search_results,
                    st.session_state.elapsed_time,
                ) = search_query(query)

        # Display results
        results = st.session_state.search_results
        elapsed_time = st.session_state.elapsed_time
    display_search_results(
        results, st.session_state["search_query"], elapsed_time
    )


if __name__ == "__main__":
    main()
