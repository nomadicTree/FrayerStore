import streamlit as st
import yaml
from dataclasses import dataclass
from app_lib.repositories import get_all_subjects_courses_topics


@dataclass
class Topic:
    code: str
    course: str
    name: str


# ----------------------------
# Data Helpers
# ----------------------------
def get_available_subjects(data):
    return sorted({row["subject"] for row in data})


def get_available_courses(data, selected_subjects):
    return sorted(
        {row["course"] for row in data if row["subject"] in selected_subjects}
    )


def get_topics_by_course(data, selected_courses):
    course_topics = {}
    for row in data:
        if row["course"] in selected_courses:
            course_topics.setdefault(row["course"], []).append(
                Topic(
                    code=row["code"],
                    course=row["course"],
                    name=row["topic_name"],
                )
            )
    return course_topics


# ----------------------------
# UI Components
# ----------------------------
def select_subjects(data):
    subjects_available = get_available_subjects(data)
    if not subjects_available:
        st.info("No subjects available.")
        st.stop()
    selected_subjects = st.multiselect(
        "Select subjects", subjects_available, default=subjects_available[0]
    )
    if not selected_subjects:
        st.info("Select at least one subject.")
        st.stop()
    return selected_subjects


def select_courses(data, selected_subjects):
    courses_available = get_available_courses(data, selected_subjects)
    if not courses_available:
        st.info("No courses for the selected subjects.")
        st.stop()
    selected_courses = st.multiselect("Select courses", courses_available)
    if not selected_courses:
        st.info("Select at least one course.")
        st.stop()
    return selected_courses


def select_topics(course_topics):
    """Return a dict mapping course -> list of selected topic codes"""
    selected_topics = {}
    for course, topics in course_topics.items():
        codes = st.multiselect(
            f"Select topics for {course}",
            options=[t.code for t in topics],
            format_func=lambda code: next(
                f"{t.code} {t.name}" for t in topics if t.code == code
            ),
        )
        selected_topics[course] = codes
    return selected_topics


def word_input_form(yaml_topics):
    """Render input fields for word data and display YAML output."""
    word = st.text_input("Word *")
    definition = st.text_area("Definition *")
    characteristics = st.text_area("Characteristics (one per line)")
    examples = st.text_area("Examples (one per line)")
    non_examples = st.text_area("Non-Examples (one per line)")

    if st.button("Generate YAML"):
        if not word or not definition:
            st.error("Word and definition are required.")
        else:
            yaml_data = {
                "word": word,
                "definition": definition,
                "characteristics": [
                    c.strip() for c in characteristics.split("\n") if c.strip()
                ],
                "examples": [
                    e.strip() for e in examples.split("\n") if e.strip()
                ],
                "non-examples": [
                    ne.strip() for ne in non_examples.split("\n") if ne.strip()
                ],
                "topics": yaml_topics,
            }
            st.code(yaml.dump(yaml_data, sort_keys=False, allow_unicode=True))


# ----------------------------
# Main
# ----------------------------
def main():
    PAGE_TITLE = "Model Maker"
    st.set_page_config(
        page_title=f"FrayerStore | {PAGE_TITLE}", page_icon="🔎"
    )
    st.title(PAGE_TITLE)
    data = get_all_subjects_courses_topics()

    selected_subjects = select_subjects(data)
    selected_courses = select_courses(data, selected_subjects)
    course_topics = get_topics_by_course(data, selected_courses)
    selected_topics = select_topics(course_topics)

    # Build YAML-ready topics
    yaml_topics = [
        {"course": course, "codes": sorted(codes)}
        for course, codes in selected_topics.items()
        if codes
    ]

    word_input_form(yaml_topics)


if __name__ == "__main__":
    main()
