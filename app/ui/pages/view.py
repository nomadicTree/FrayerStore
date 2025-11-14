import streamlit as st
from app.core.models.word_models import WordVersionChoice, WordVersion
from app.core.respositories.words_repo import get_word_full
from app.ui.components.page_header import page_header
from app.ui.components.selection_helpers import select_item
from app.ui.components.frayer import (
    render_frayer_model,
)


# --------------------------------------------------------------------
# Query parameter utilities
# --------------------------------------------------------------------
def get_word_from_query_params():
    """Extract the 'id' parameter from the query string and return the Word object."""
    id_param = st.query_params.get("id")

    if id_param is None:
        st.info("No id given in URL. Are you here accidentally?")
        return None

    try:
        word_id = int(id_param)
    except ValueError:
        st.error("Invalid id in URL")
        st.stop()

    word = get_word_full(word_id)
    if word is None:
        st.error(f"No word found with id {word_id}")
        st.stop()

    return word


def get_query_param_single(name: str) -> str | None:
    """Safely extract a single value from Streamlit's query parameters."""
    value = st.query_params.get(name)
    if isinstance(value, list):
        return value[0]
    return value


# --------------------------------------------------------------------
# Sidebar rendering
# --------------------------------------------------------------------
def render_sidebar(word) -> (WordVersion, dict):
    """Render sidebar controls and return user display preferences."""
    with st.sidebar:
        choices = [WordVersionChoice(v) for v in word.versions]
        selected_level = select_item(items=choices, key="level", label="Select level")
        version = selected_level.version

        st.write("Toggle visibility:")
        options = {
            "show_word": st.checkbox("Word", value=True, key="show_word"),
            "show_definition": st.checkbox(
                "Definition", value=True, key="show_definition"
            ),
            "show_characteristics": st.checkbox(
                "Characteristics", value=True, key="show_characteristics"
            ),
            "show_examples": st.checkbox("Examples", value=True, key="show_examples"),
            "show_non_examples": st.checkbox(
                "Non-examples", value=True, key="show_non_examples"
            ),
            # placeholders; will fill below
            "show_related_words": False,
            "show_topics": False,
        }

        # --- Related words BEFORE Topics ---
        if word.related_words:
            options["show_related_words"] = st.checkbox(
                "Related words",
                value=True,
                key="show_related_words",
            )

        options["show_topics"] = st.checkbox(
            "Topics",
            value=True,
            key="show_topics",
        )

        return version, options


# --------------------------------------------------------------------
# Main view
# --------------------------------------------------------------------
def main():
    word = get_word_from_query_params()
    if word is None:
        st.stop()

    version, view_options = render_sidebar(word)

    displayed_word_header = version.word if view_options["show_word"] else "❓"
    page_header("Frayer Model", f"**{word.subject.name}:** {displayed_word_header}")

    if version:
        render_frayer_model(
            version,
            show_word=view_options["show_word"],
            related_words=word.related_words,
            show_topics=view_options["show_topics"],
            show_definition=view_options["show_definition"],
            show_characteristics=view_options["show_characteristics"],
            show_examples=view_options["show_examples"],
            show_non_examples=view_options["show_non_examples"],
            show_related_words=view_options["show_related_words"],
        )


if __name__ == "__main__":
    main()
