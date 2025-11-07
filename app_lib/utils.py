import streamlit as st
import pandas as pd
import re
import unicodedata


def list_to_md(items):
    """Convert a list of strings to a markdown bullet list."""
    return "\n".join(f"- {item}" for item in items)


def render_topics(topics, word_id):
    topics_frame = pd.DataFrame(topics)
    column_config = {
        "code": st.column_config.Column("Code", width="auto"),
        "topic_name": st.column_config.Column("Topic", width="auto"),
        "course_name": st.column_config.Column("Course"),
    }
    st.dataframe(
        topics_frame,
        hide_index=True,
        column_order=("course_name", "code", "topic_name"),
        column_config=column_config,
        key=f"topic_frame_{word_id}",
    )


def render_frayer(
    word_id,
    word,
    definition,
    characteristics,
    examples,
    non_examples,
    subject_name=None,
    topics=None,
    show_link=False,
):
    word_url = f"/View?id={word_id}"
    if show_link:
        st.markdown(
            f"""
            <div class="frayer-title">
                <h3>
                    <a href="{word_url}" target="_blank" class="word-link">
                        {word} <span class="open-link-icon">🔗</span>
                    </a>
                </h3>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.subheader(word)
    # Optional subject/courses display
    if subject_name:
        st.caption(f"Subject: **{subject_name}**")
    col1, col2 = st.columns(2, border=True)
    with col1:
        st.markdown("#### Definition")
        st.write(definition)
    with col2:
        st.markdown("#### Characteristics")
        st.markdown(list_to_md(characteristics))

    col1, col2 = st.columns(2, border=True)
    with col1:
        st.markdown("#### Examples")
        st.markdown(list_to_md(examples))
    with col2:
        st.markdown("#### Non-examples")
        st.markdown(list_to_md(non_examples))

    if topics:
        st.markdown("##### Topics:")
        render_topics(topics, word_id)


def safe_snake_case_filename(s: str, extension) -> str:
    # Normalize unicode characters to ASCII equivalents
    s = (
        unicodedata.normalize("NFKD", s)
        .encode("ascii", "ignore")
        .decode("ascii")
    )

    # Replace illegal filename characters with underscore
    s = re.sub(r'[\/\\\:\*\?"<>\|]', "_", s)

    # Replace spaces, hyphens, and dots with underscore
    s = re.sub(r"[\s\-.]+", "_", s)

    # Add underscore before uppercase letters (CamelCase → snake_case)
    s = re.sub(r"(?<!^)(?=[A-Z])", "_", s)

    # Lowercase everything
    s = s.lower()

    # Collapse multiple underscores
    s = re.sub(r"_+", "_", s)

    # Strip leading/trailing underscores
    return f"{s.strip("_")}.{extension}"


def apply_styles():
    st.html(
        """
    <style>
    [data-testid='stHeaderActionElements'] {display: none;}
    .open-link-icon {
        text-decoration: none !important;
        opacity: 0;
        transition: opacity 0.2s;
        cursor: pointer;
    }

    .frayer-title .word-link {
        text-decoration: none !important;
        color: inherit;
        position: relative;
    }

    .frayer-title:hover .open-link-icon {
        opacity: 1;
    }
    </style>
    """
    )
