import sqlite3
from frayerstore.db.interfaces.topic_repo import TopicRepository


class SQLiteTopicRepository(TopicRepository):
    def __init__(self, conn: sqlite3.Connection, mapper):
        self.conn = conn
        self.mapper = mapper

    def get_by_slug(self, slug: str):
        row = self.conn.execute("SELECT * FROM Topics WHERE slug=?", (slug,)).fetchone()
        return self.mapper.row_to_domain(row) if row else None

    def get_by_name(self, name: str):
        # Needed for generic importer only — but topics shouldn't use name for lookup
        row = self.conn.execute("SELECT * FROM Topics WHERE name=?", (name,)).fetchone()
        return self.mapper.row_to_domain(row) if row else None

    def get_by_course_and_code(self, course_pk: int, code: str):
        row = self.conn.execute(
            "SELECT * FROM Topics WHERE course_id=? AND code=?",
            (course_pk, code),
        ).fetchone()
        return self.mapper.row_to_domain(row) if row else None

    def get_by_id(self, pk: int):
        row = self.conn.execute("SELECT * FROM Topics WHERE id=?", (pk,)).fetchone()
        return self.mapper.row_to_domain(row) if row else None

    def create(self, data):
        params = self.mapper.create_to_params(data)
        row = self.conn.execute(
            """
            INSERT INTO Topics (course_id, code, name, slug)
            VALUES (?, ?, ?, ?)
            RETURNING id, course_id, code, name, slug
            """,
            params,
        ).fetchone()
        return self.mapper.row_to_domain(row)
