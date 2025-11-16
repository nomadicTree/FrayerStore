import streamlit as st
import string
from app.ui.components.page_header import page_header
from app.core.respositories.courses_repo import get_courses
from app.ui.components.selection_helpers import select_course
from app.core.respositories.words_repo import get_word_versions_for_course
from app.ui.components.frayer import render_frayer_model
from app.ui.components.buttons import wordversion_details_button

PAGE_TITLE = "Course Glossary"


def wordversion_expander(wv):
    with st.expander(wv.word, expanded=False):
        render_frayer_model(wv)
        wordversion_details_button(wv)


def main():
    all_courses = get_courses()
    with st.sidebar:
        course = select_course(all_courses)

    page_header(PAGE_TITLE)

    course_word_versions = get_word_versions_for_course(course)
    course_word_versions.sort()

    groups = {letter: [] for letter in string.ascii_uppercase}
    groups["#"] = []  # for everything non-alphabetic

    for wv in course_word_versions:
        first = wv.word[0].upper()
        key = first if first in groups else "#"
        groups[key].append(wv)

    for letter in string.ascii_uppercase:
        items = groups[letter]
        if not items:
            continue

        st.subheader(letter)

        for wv in items:
            wordversion_expander(wv)

    if groups["#"]:
        st.subheader("#")
        for wv in groups["#"]:
            wordversion_expander(wv)


if __name__ == "__main__":
    main()
