import sqlite3
from frayerstore.db.interfaces.course_repo import CourseRepository


class SQLiteCourseRepository(CourseRepository):
    def __init__(self, conn: sqlite3.Connection, mapper):
        self.conn = conn
        self.mapper = mapper

    def get_by_slug(self, slug: str):
        row = self.conn.execute(
            "SELECT * FROM Courses WHERE slug=?", (slug,)
        ).fetchone()
        return self.mapper.row_to_domain(row) if row else None

    def get_by_name(self, name: str):
        row = self.conn.execute(
            "SELECT * FROM Courses WHERE name=?", (name,)
        ).fetchone()
        return self.mapper.row_to_domain(row) if row else None

    def get_by_id(self, pk: int):
        row = self.conn.execute("SELECT * FROM Courses WHERE id=?", (pk,)).fetchone()
        return self.mapper.row_to_domain(row) if row else None

    def create(self, data):
        params = self.mapper.create_to_params(data)
        row = self.conn.execute(
            """
            INSERT INTO Courses (subject_id, level_id, name, slug)
            VALUES (?, ?, ?, ?)
            RETURNING id, subject_id, level_id, name, slug
            """,
            params,
        ).fetchone()
        return self.mapper.row_to_domain(row)
