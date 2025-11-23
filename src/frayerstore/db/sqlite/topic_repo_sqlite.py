import sqlite3
from typing import Any
from frayerstore.db.interfaces.topic_repo import TopicRepository
from frayerstore.models.topic import Topic


class SQLiteTopicRepository(TopicRepository):
    def __init__(self, conn: sqlite3.Connection, topic_mapper):
        self.conn = conn
        self.topic_mapper = topic_mapper

    def _get_one(self, where: str, param: Any) -> Topic | None:
        """
        Internal lookup helper for all Topic retrieval methods.

        Return None if no topic matches the condition.
        """
        q = f"""
            SELECT id, name, code, slug, course_id
            FROM Topics
            WHERE {where}
        """

        params = param if isinstance(param, tuple) else (param,)
        row = self.conn.execute(q, params).fetchone()

        if not row:
            return None

        return self.topic_mapper.row_to_domain(row)

    def _get_many(
        self,
        where: str | None = None,
        params: tuple = (),
    ) -> list[Topic]:
        """
        Internal helper for retrieving multiple Topic objects.

        - If `where` is None, all topics are returned.
        - Results are ordered alphabetically by topic code.

        Returns:
            A list of Topic objects (possibly empty).
        """
        base_q = """
            SELECT
                id,
                name,
                code,
                slug,
                course_id
            FROM Topics
        """

        if where:
            q = f"{base_q} WHERE {where}"
        else:
            q = base_q

        q += " ORDER BY code ASC"

        rows = self.conn.execute(q, params).fetchall()
        return [self.topic_mapper.row_to_domain(r) for r in rows]

    def get_by_slug(self, slug: str) -> Topic:
        """Retrieve Topic by slug."""
        return self._get_one("slug = ?", slug)

    def get_by_name(self, name: str) -> Topic:
        """Retrieve Topic by name."""
        return self._get_one("name = ?", name)

    def get_by_id(self, id: int) -> Topic:
        """Retrieve Topic by id."""
        return self._get_one("id = ?", id)

    def get_by_course_and_code(self, course_id: int, code: str) -> Topic | None:
        """Retrieve Topic by course id and topic code."""
        return self._get_one("course_id = ? AND code = ?", (course_id, code))

    def list_all(self) -> list[Topic]:
        """Return all topics."""
        return self._get_many()

    def get_for_course(self, course_id: int) -> list[Topic]:
        """
        Retrieve all topics for a given course, ordered by code.
        """
        q = """
            SELECT
                id,
                name,
                code,
                slug,
                course_id
            FROM Topics
            WHERE course_id = ?
            ORDER BY code ASC
        """
        rows = self.conn.execute(q, (course_id,)).fetchall()
        return [self.topic_mapper.row_to_domain(r) for r in rows]

    def create(self, data):
        params = self.topic_mapper.create_to_params(data)
        row = self.conn.execute(
            """
            INSERT INTO Topics (course_id, code, name, slug)
            VALUES (?, ?, ?, ?)
            RETURNING id, course_id, code, name, slug
            """,
            params,
        ).fetchone()
        return self.topic_mapper.row_to_domain(row)
