from pathlib import Path
import streamlit as st


def show_markdown_file(file_path: Path, in_container: bool = False):
    """Write the contents of a markdown file to the page, displaying it as HTML

    Args:
        file_path: path to the file
        in_container: If True, display the file contents in a container with a border. Defaults to False.
    """
    md_text = Path(file_path).read_text(encoding="utf-8")
    if in_container:
        with st.container(border=True):
            st.markdown(md_text)
    else:
        st.markdown(md_text)
