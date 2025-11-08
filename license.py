import streamlit as st
from pathlib import Path
from app_lib.utils import page_header

PAGE_TITLE = "Licensing"


def show_markdown_file(file_path: Path):
    md_text = Path(file_path).read_text(encoding="utf-8")
    st.markdown(md_text, unsafe_allow_html=True)


def main():
    page_header(PAGE_TITLE)

    st.subheader("Content license")
    show_markdown_file(Path("LICENSE_CONTENT.md"))
    st.subheader("Code license")
    show_markdown_file(Path("LICENSE.md"))


if __name__ == "__main__":
    main()
