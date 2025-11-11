"""Data access helpers for academic hierarchy objects.

These helpers return instances of the domain models (Subject, Course, Topic,
and Level) so that the rest of the application can work with structured
objects instead of raw database rows.
"""

from __future__ import annotations

from collections.abc import Iterable

import streamlit as st

from app.core.db import get_db
from app.core.models.course_model import Course
from app.core.models.level_model import Level
from app.core.models.subject_model import Subject
from app.core.models.topic_model import Topic


def _row_to_level(row) -> Level | None:
    if row["level_id"] is None:
        return None
    return Level(row["level_id"], row["level_name"], row["level_description"])


@st.cache_data(show_spinner=False)
def get_all_subjects() -> list[Subject]:
    """Return all subjects in alphabetical order."""

    db = get_db()
    rows = db.execute(
        "SELECT id AS subject_id, name AS subject_name FROM Subjects "
        "ORDER BY name COLLATE NOCASE"
    ).fetchall()
    return [Subject(row["subject_id"], row["subject_name"]) for row in rows]


@st.cache_data(show_spinner=False)
def get_subject_by_id(subject_id: int) -> Subject | None:
    """Return a single subject by its primary key."""

    db = get_db()
    row = db.execute(
        "SELECT id AS subject_id, name AS subject_name FROM Subjects WHERE id = ?",
        (subject_id,),
    ).fetchone()
    return Subject(row["subject_id"], row["subject_name"]) if row else None


@st.cache_data(show_spinner=False)
def get_courses_for_subject(subject_id: int) -> list[Course]:
    """Return all courses belonging to the given subject."""

    db = get_db()
    rows = db.execute(
        """
        SELECT
            c.id   AS course_id,
            c.name AS course_name,
            s.id   AS subject_id,
            s.name AS subject_name,
            l.id   AS level_id,
            l.name AS level_name,
            l.description AS level_description
        FROM Courses c
        JOIN Subjects s ON c.subject_id = s.id
        LEFT JOIN Levels l ON c.level_id = l.id
        WHERE c.subject_id = ?
        ORDER BY c.name COLLATE NOCASE
        """,
        (subject_id,),
    ).fetchall()

    if not rows:
        return []

    subject = Subject(rows[0]["subject_id"], rows[0]["subject_name"])

    courses: list[Course] = []
    for row in rows:
        level = _row_to_level(row)
        courses.append(Course(row["course_id"], row["course_name"], subject, level))
    return courses


@st.cache_data(show_spinner=False)
def get_topics_for_course(course_id: int) -> list[Topic]:
    """Return all topics for the given course."""

    db = get_db()
    rows = db.execute(
        """
        SELECT
            t.id   AS topic_id,
            t.code AS topic_code,
            t.name AS topic_name,
            c.id   AS course_id,
            c.name AS course_name,
            s.id   AS subject_id,
            s.name AS subject_name,
            l.id   AS level_id,
            l.name AS level_name,
            l.description AS level_description
        FROM Topics t
        JOIN Courses c ON t.course_id = c.id
        JOIN Subjects s ON c.subject_id = s.id
        LEFT JOIN Levels l ON c.level_id = l.id
        WHERE t.course_id = ?
        ORDER BY t.code COLLATE NOCASE, t.name COLLATE NOCASE
        """,
        (course_id,),
    ).fetchall()

    if not rows:
        return []

    subject = Subject(rows[0]["subject_id"], rows[0]["subject_name"])
    level = _row_to_level(rows[0])
    course = Course(rows[0]["course_id"], rows[0]["course_name"], subject, level)

    topics: list[Topic] = []
    for row in rows:
        topics.append(Topic(row["topic_id"], row["topic_code"], row["topic_name"], course))
    return topics


def find_subject_by_name(subjects: Iterable[Subject], name: str) -> Subject | None:
    """Return the first subject with the provided name."""

    return next((subject for subject in subjects if subject.name == name), None)


def find_course_by_name(courses: Iterable[Course], name: str) -> Course | None:
    """Return the first course with the provided name."""

    return next((course for course in courses if course.name == name), None)
