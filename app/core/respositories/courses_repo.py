import streamlit as st
import datetime
from app.core.db import get_db
from app.core.models.course_model import Course
from app.core.models.level_model import Level
from app.core.models.subject_model import Subject


@st.cache_data(ttl=datetime.timedelta(hours=1))
def get_courses() -> list[Course]:
    """Get all Courses with their Subject and Level objects."""
    db = get_db()
    q = """
        SELECT
            c.id AS course_id,
            c.name AS course_name,
            s.id AS subject_id,
            s.name AS subject_name,
            l.id AS level_id,
            l.name AS level_name,
            l.description AS level_description
        FROM Courses AS c
        JOIN Subjects AS s ON c.subject_id = s.id
        LEFT JOIN Levels AS l ON c.level_id = l.id
        ORDER BY s.name, l.name, c.name
    """
    rows = db.execute(q).fetchall()

    courses = []
    for r in rows:
        subject = Subject(r["subject_id"], r["subject_name"])
        level = (
            Level(r["level_id"], r["level_name"], r["level_description"])
            if r["level_id"]
            else None
        )
        course = Course(
            course_id=r["course_id"],
            name=r["course_name"],
            subject=subject,
            level=level,
        )
        courses.append(course)

    return courses
