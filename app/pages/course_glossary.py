import streamlit as st
from app_lib.models import Word
from app_lib.repositories import (
    get_all_subjects_courses_topics,
    get_words_by_topic,
)
from app.components.selection_helpers import select_subject, select_course
from app.components.common import page_header

PAGE_TITLE = "Course Glossary"


def get_words_for_course(data, subject, course):
    if subject is None or course is None:
        return []
    all_words = []
    all_words_set = set()
    for row in data:
        if row["subject"] == subject.name and row["course"] == course.name:
            topic_id = row["topic_id"]
            for w in get_words_by_topic(topic_id) or []:
                if w["word"] not in all_words_set:
                    all_words_set.add(w["word"])
                    all_words.append(Word(w))
    if not all_words:
        st.info("No words available for this course.")
        st.stop()
    return sorted(all_words, key=lambda w: w.word.lower())


def display_words(words):
    for w in words:
        with st.expander(w.word, expanded=False):
            render_frayer(w.as_dict(), show_topics=True)


def main():
    page_header(PAGE_TITLE)

    with st.spinner("Loading..."):
        data = get_all_subjects_courses_topics()
    subject = select_subject()
    if subject is None:
        st.stop()

    course = select_course(subject)
    if course is None:
        st.stop()
    st.divider()

    with st.spinner("Loading..."):
        words = get_words_for_course(data, subject, course)
    display_words(words)


if __name__ == "__main__":
    main()
