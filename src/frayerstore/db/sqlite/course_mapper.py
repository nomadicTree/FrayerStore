from __future__ import annotations
import sqlite3
from frayerstore.models.course import Course
from frayerstore.models.course_create import CourseCreate
from frayerstore.db.sqlite.level_mapper import LevelMapper


class CourseMapper:
    def __init__(self, level_mapper: LevelMapper) -> CourseMapper:
        self.level_mapper = level_mapper

    def row_to_domain(self, row: sqlite3.Row) -> Course:
        return Course(
            pk=row["course_id"],
            name=row["course_name"],
            slug=row["course_slug"],
            subject_pk=row["subject_id"],
            level=self.level_mapper.from_joined_row(row),
        )

    def create_to_params(self, data: CourseCreate) -> tuple:
        return (data.subject_pk, data.level_pk, data.name, data.slug)
