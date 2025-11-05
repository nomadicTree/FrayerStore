import streamlit as st
import json
import markdown


def concise_html_list(list):
    list_html = f"""<ul style="margin:0; padding-left:20px;">
        {''.join(f'<li>{i}</li>' for i in list)}
    </ul>"""
    return list_html


def list_to_md(items):
    """Convert a list of strings to a markdown bullet list."""
    return "\n".join(f"- {item}" for item in items)


def md_to_html(md_text):
    """Convert markdown to HTML using python-markdown with useful extensions."""
    # extensions 'extra' and 'sane_lists' help render lists/inline code well.
    # If you expect raw HTML in the markdown and want to allow it, remove the html.escape() below.
    return markdown.markdown(md_text, extensions=["extra", "sane_lists"])


class Word:
    def __init__(self, row):
        self.id = row["id"]
        self.word = row["word"]
        self.definition = (
            row["definition"] if "definition" in row.keys() else ""
        )
        self.characteristics = (
            json.loads(row["characteristics"])
            if "characteristics" in row.keys()
            else []
        )
        self.examples = (
            json.loads(row["examples"]) if "examples" in row.keys() else []
        )
        self.non_examples = (
            json.loads(row["non_examples"])
            if "non_examples" in row.keys()
            else []
        )
        self.subject_name = (
            row["subject_name"] if "subject_name" in row.keys() else None
        )
        self.courses = (
            row["courses"].split("||") if "courses" in row.keys() else ""
        )

        self.topics = (
            row["topics"].split("||") if "topics" in row.keys() else ""
        )

    def display_frayer(self, include_subject_info=False, show_topics=False):
        if include_subject_info:
            st.write(f"{", ".join(self.courses)}")

        frayer_html = f"""
        <div class="frayer-grid">
            <div class="frayer-cell">
                <div class="frayer-title">Definition</div>
                {self.definition}
            </div>
            <div class="frayer-cell">
                <div class="frayer-title">Characteristics</div>
                {md_to_html(list_to_md(self.characteristics))}
            </div>
            <div class="frayer-cell">
                <div class="frayer-title">Examples</div>
                {md_to_html(list_to_md(self.examples))}
            </div>
            <div class="frayer-cell">
                <div class="frayer-title">Non-Examples</div>
                {md_to_html(list_to_md(self.non_examples))}
            </div>
        </div>
        """
        st.markdown(frayer_html, unsafe_allow_html=True)

        if show_topics:
            if self.topics:
                st.markdown("**Topics:**")
                st.markdown(
                    concise_html_list(self.topics), unsafe_allow_html=True
                )
                st.write("######")
