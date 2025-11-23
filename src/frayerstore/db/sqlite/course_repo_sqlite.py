import sqlite3
from typing import Any
from frayerstore.db.interfaces.course_repo import CourseRepository
from frayerstore.db.interfaces.topic_repo import TopicRepository
from frayerstore.db.sqlite.course_mapper import CourseMapper
from frayerstore.models.course import Course


class SQLiteCourseRepository(CourseRepository):
    def __init__(
        self,
        conn: sqlite3.Connection,
        course_mapper: CourseMapper,
        topic_repo: TopicRepository,
    ):
        self.conn = conn
        self.course_mapper = course_mapper
        self.topic_repo = topic_repo

    def _get_one(self, where: str, param: Any, include_topics: bool) -> Course | None:
        """
        Internal lookup helper for all Course retrieval methods.

        Hydration behaviour:
        - If include_topics=True:
            course.topics will contain a fully hydrated list of Topic objects.

        - If include_topics=False
            course.topics will be an empty list.

        Returns None if no courses matches the condition.
        """
        q = f"""
            SELECT
                c.id as course_id,
                c.name as course_name,
                c.slug as course_slug,
                c.subject_id as subject_id,
                l.id as level_id,
                l.name as level_name,
                l.slug as level_slug
            FROM Courses c
            JOIN Levels l on l.id = c.level_id
            WHERE {where}
        """
        row = self.conn.execute(q, (param,)).fetchone()

        if not row:
            return None

        course = self.course_mapper.row_to_domain(row)

        if include_topics:
            course.topics = self.topic_repo.get_for_course(course.pk)

        return course

    def _get_many(
        self,
        where: str | None = None,
        params: tuple = (),
        include_topics: bool = False,
    ) -> list[Course]:
        """
        Internal helper for retrieving multiple Course objects.

        Query behaviour:
        - Always joins Levels to fully hydrate the `level` field on each Course.
        - The `where` clause and its `params` control filtering. If `where` is None,
        all courses are returned.
        - Results are ordered alphabetically by course name.

        Hydration behaviour:
        - If include_topics=False:
            each returned Course will have an empty `topics` list.
        - If include_topics=True:
            each returned Course will have its `topics` list populated
            with fully hydrated Topic objects via TopicRepository.get_for_course().

        Returns:
            A list of fully hydrated Course objects (possibly empty).
        """
        base_q = """
            SELECT
                c.id   AS course_id,
                c.name AS course_name,
                c.slug AS course_slug,
                c.subject_id AS subject_id,

            l.id   AS level_id,
            l.name AS level_name,
            l.slug AS level_slug

            FROM Courses c
            JOIN Levels l ON l.id = c.level_id
        """

        if where:
            q = base_q + f" WHERE {where}"
        else:
            q = base_q

        q += " ORDER BY c.name ASC"

        rows = self.conn.execute(q, params).fetchall()

        courses = [self.course_mapper.row_to_domain(r) for r in rows]

        if include_topics:
            for course in courses:
                course.topics = self.topic_repo.get_for_course(course.pk)

        return courses

    def get_by_slug(self, slug: str, include_topics: bool = False):
        """Retrieve a Course by slug."""
        return self._get_one("c.slug = ?", slug, include_topics)

    def get_by_name(self, name: str, include_topics: bool = False):
        """Retrieve a Course by name."""
        return self._get_one("c.name = ?", name, include_topics)

    def get_by_id(self, id: int, include_topics: bool = False):
        """Retrieve a Course by id."""
        return self._get_one("c.id = ?", id, include_topics)

    def get_for_subject(
        self,
        subject_id: int,
        include_topics: bool = False,
    ) -> list[Course]:
        """Return all courses that belong to the given subject."""
        return self._get_many(
            where="c.subject_id = ?",
            params=(subject_id,),
            include_topics=include_topics,
        )

    def list_all(self, include_topics: bool = False) -> list[Course]:
        """Return all courses."""
        return self._get_many(
            where=None,
            params=(),
            include_topics=include_topics,
        )

    def create(self, data):
        params = self.course_mapper.create_to_params(data)
        q = """
            INSERT INTO Courses (subject_id, level_id, name, slug)
            VALUES (?, ?, ?, ?)
        """
        cur = self.conn.execute(q, params)
        course_id = cur.lastrowid
        return self.get_by_id(course_id, include_topics=False)
