import streamlit as st
from app_lib.repositories import search_words


@st.cache_data
def get_word_object(row_dict):
    # ensures Word() creation is cached per unique row
    from app_lib.models import Word

    return Word(row_dict)


def search_query(query):
    word_rows = search_words(query)
    return [get_word_object(dict(r)) for r in word_rows]


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


st.set_page_config(page_title="FrayerStore")
st.title("Search")

# --- Step 1: Read query from URL ---
query = st.query_params.get("q", [""])[0]

# --- Step 2: Search input controlled by URL ---
query = st.text_input("Search FrayerStore", value=query).strip()

# --- Step 3: Update URL if input changed ---
st.query_params = {"q": [query]}

# --- Step 4: Run search ---
results = search_query(query) if query else []

# --- Step 5: Display results ---
for word in results:
    with st.expander(f"{word.word} – {word.subject_name}", expanded=False):
        word.display_frayer(include_subject_info=True, show_topics=True)
