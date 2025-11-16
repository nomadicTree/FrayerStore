"""Streamlit page for searching the words database"""

import re
import time
import streamlit as st
from app.services.search.search_service import search_words
from app.core.utils.strings import format_time_text
from app.ui.components.page_header import page_header
from app.ui.components.buttons import searchhit_details_button
from app.services.search.search_models import SearchFilters, SearchHit
from app.core.respositories.subjects_repo import get_all_subjects
from app.core.respositories.levels_repo import get_all_levels
from app.services.search.search_service import get_subject_level_map
from app.ui.components.selection_helpers import select_one

PAGE_TITLE = "Search"


def select_search_filters():
    subjects = get_all_subjects()
    levels = get_all_levels()
    mapping = get_subject_level_map()

    # Select subject
    subject = select_one(sorted(subjects), key="subject", label="Subject")

    # Levels depend on subject
    if subject:
        allowed = mapping.get(subject.pk, set())
        level_options = [lvl for lvl in levels if lvl.name in allowed]
    else:
        level_options = levels

    level = select_one(sorted(level_options), key="levels", label="Level")

    return SearchFilters(subject=subject, level=level)


@st.cache_data(show_spinner=False)
def search_query(query: str, filters: SearchFilters):
    """Return matching words and search duration."""
    start_time = time.perf_counter()
    results = search_words(query, filters)
    elapsed = time.perf_counter() - start_time
    return results, elapsed


def underline_matches(text: str, query: str) -> str:
    """Underline all case-insensitive occurrences of query inside text."""
    q = query.strip()
    if not q:
        return text

    pattern = re.compile(re.escape(q), re.IGNORECASE)
    return pattern.sub(lambda m: f"<u>{m.group(0)}</u>", text)


def display_search_hit(hit: SearchHit, query: str):
    with st.container(border=True):
        # --- underline matches in the word itself ---
        highlighted_word = underline_matches(hit.word, query)
        st.markdown(f"#### {highlighted_word}", unsafe_allow_html=True)

        # --- underline matches in synonyms ---
        if hit.synonyms:
            highlighted_syns = ", ".join(
                underline_matches(s, query) for s in hit.synonyms
            )
            st.markdown(f"**Synonyms:** {highlighted_syns}", unsafe_allow_html=True)

        # plain definition
        if hit.version_definition:
            st.write(hit.version_definition)

        # link to full view
        searchhit_details_button(hit)


def display_search_results(results: list[SearchHit], query: str, elapsed: float):
    if not query:
        return

    plural = "s" if len(results) != 1 else ""
    st.caption(
        f"Found {len(results)} result{plural} for {query!r} in {format_time_text(elapsed)}."
    )

    if not results:
        st.info(f"No results found for {query!r}.")
        return

    for hit in results:
        display_search_hit(hit, query)


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

    with st.sidebar:
        filters = select_search_filters()

    # Search input
    query = st.text_input(
        "Search FrayerStore",
        value=st.session_state.search_query,
        key="search_input",
    ).strip()

    st.divider()

    with st.spinner("Searching..."):
        # Perform search only if the query changed
        if query and query != st.session_state.search_query:
            st.session_state.search_query = query
            if query:
                (
                    st.session_state.search_results,
                    st.session_state.elapsed_time,
                ) = search_query(query, filters)

        # Display results
    display_search_results(
        st.session_state.search_results,
        st.session_state["search_query"],
        st.session_state.elapsed_time,
    )


if __name__ == "__main__":
    main()
