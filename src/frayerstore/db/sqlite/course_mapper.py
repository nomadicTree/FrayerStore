import sqlite3
from frayerstore.models.course import Course
from frayerstore.models.course_create import CourseCreate


class CourseMapper:
    def row_to_domain(self, row: sqlite3.Row) -> Course:
        return Course(
            pk=row["id"],
            subject_pk=row["subject_id"],
            level_pk=row["level_id"],
            name=row["name"],
            slug=row["slug"],
        )

    def create_to_params(self, data: CourseCreate) -> tuple:
        return (data.subject_pk, data.level_pk, data.name, data.slug)
