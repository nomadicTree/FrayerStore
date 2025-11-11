from __future__ import annotations

import streamlit as st

from app.core.models.course_model import Course
from app.core.models.subject_model import Subject
from app.core.respositories import (
    find_course_by_name,
    find_subject_by_name,
    get_all_subjects,
    get_courses_for_subject,
)


def _reset_course_selection():
    st.session_state.pop("selected_course_id", None)
    st.session_state.pop("selected_course_subject_id", None)


def select_subject() -> Subject | None:
    subjects = get_all_subjects()
    if not subjects:
        st.info("No subjects available.")
        return None

    subject_names = [s.name for s in subjects]
    query_subject = st.query_params.get("subject")

    selected_subject = None
    if query_subject:
        selected_subject = find_subject_by_name(subjects, query_subject)

    if not selected_subject:
        stored_id = st.session_state.get("selected_subject_id")
        if stored_id is not None:
            selected_subject = next(
                (s for s in subjects if s.subject_id == stored_id), None
            )

    if not selected_subject:
        selected_subject = subjects[0]

    current_id = st.session_state.get("selected_subject_id")
    if current_id != selected_subject.subject_id:
        st.session_state["selected_subject_id"] = selected_subject.subject_id
        _reset_course_selection()

    selected_index = subject_names.index(selected_subject.name)
    selected_name = st.selectbox(
        "Select subject",
        subject_names,
        index=selected_index,
    )
    selected_subject = find_subject_by_name(subjects, selected_name)

    if selected_subject is None:
        return None

    if st.session_state.get("selected_subject_id") != selected_subject.subject_id:
        st.session_state["selected_subject_id"] = selected_subject.subject_id
        _reset_course_selection()

    if query_subject != selected_name:
        st.query_params["subject"] = selected_name
        st.rerun()

    return selected_subject


def select_course(subject: Subject | None) -> Course | None:
    if subject is None:
        return None

    courses = get_courses_for_subject(subject.subject_id)
    if not courses:
        st.info("No courses for this subject.")
        return None

    course_names = [c.name for c in courses]
    query_course = st.query_params.get("course")

    selected_course = None
    if query_course:
        selected_course = find_course_by_name(courses, query_course)

    prev_subject_id = st.session_state.get("selected_course_subject_id")
    if prev_subject_id != subject.subject_id:
        st.session_state.pop("selected_course_id", None)

    if not selected_course:
        stored_id = st.session_state.get("selected_course_id")
        if stored_id is not None:
            selected_course = next(
                (c for c in courses if c.course_id == stored_id), None
            )

    if not selected_course:
        selected_course = courses[0]

    selected_index = course_names.index(selected_course.name)
    selected_name = st.selectbox(
        "Select course",
        course_names,
        index=selected_index,
    )

    selected_course = find_course_by_name(courses, selected_name)
    if selected_course is None:
        return None

    st.session_state["selected_course_id"] = selected_course.course_id
    st.session_state["selected_course_subject_id"] = subject.subject_id

    if query_course != selected_name:
        st.query_params["course"] = selected_name
        st.rerun()

    return selected_course
