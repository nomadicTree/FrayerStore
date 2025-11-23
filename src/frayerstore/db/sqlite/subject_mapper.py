import sqlite3
from frayerstore.models.subject import Subject
from frayerstore.models.subject_create import SubjectCreate


class SubjectMapper:
    def row_to_domain(self, row: sqlite3.Row) -> Subject:
        """Convert a subject row to Subject object."""
        return Subject(pk=row["id"], name=row["name"], slug=row["slug"])

    def create_to_params(self, data: SubjectCreate) -> tuple:
        return (data.name, data.slug)
