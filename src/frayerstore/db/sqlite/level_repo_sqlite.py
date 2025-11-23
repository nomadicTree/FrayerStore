from __future__ import annotations
import sqlite3
from typing import Any
from frayerstore.models.level import Level
from frayerstore.models.level_create import LevelCreate
from frayerstore.db.interfaces.level_repo import LevelRepository
from frayerstore.db.sqlite.level_mapper import LevelMapper


class SQLiteLevelRepository(LevelRepository):
    def __init__(
        self, conn: sqlite3.Connection, mapper: LevelMapper
    ) -> SQLiteLevelRepository:
        self.conn = conn
        self.mapper = mapper

    def _get_one(self, where: str, param: Any) -> Level:
        """
        Internal lookup helper for all Level retrieval methods.

        Returns None of no level matches the condition.
        """
        q = f"""
            SELECT id, name, slug
            FROM Levels
            WHERE {where}
        """
        row = self.conn.execute(q, (param,)).fetchone()
        if not row:
            return None

        level = self.mapper.row_to_domain(row)
        return level

    def _get_many(
        self,
        where: str | None = None,
        params: tuple = (),
    ) -> list[Level]:
        """
        Internal helper for retrieving multiple Level objects.

        - If `where` is None, all levels are returned.
        - Results are ordered alphabetically by level name.

        Returns:
            A list of Level objects (possibly empty).
        """
        base_q = """
            SELECT
                id,
                name,
                slug
            FROM Levels
        """

        if where:
            q = f"{base_q} WHERE {where}"
        else:
            q = base_q

        q += " ORDER BY name ASC"

        rows = self.conn.execute(q, params).fetchall()

        return [self.mapper.row_to_domain(r) for r in rows]

    def get_by_slug(self, slug: str) -> Level:
        """Retrieve a Level by slug."""
        return self._get_one("slug = ?", slug)

    def get_by_name(self, name: str) -> Level:
        """Retrieve a Level by slug."""
        return self._get_one("name = ?", name)

    def get_by_id(self, id: str) -> Level:
        """Retrieve a Level by slug."""
        return self._get_one("id = ?", id)

    def list_all(self) -> list[Level]:
        """Return all levels."""
        return self._get_many()

    def create(self, data: LevelCreate) -> Level:
        params = self.mapper.create_to_params(data)
        q = """
        INSERT INTO Levels (name, slug)
        VALUES (?, ?)
        RETURNING id, name, slug
        """
        row = self.conn.execute(q, params).fetchone()
        return self.mapper.row_to_domain(row)
