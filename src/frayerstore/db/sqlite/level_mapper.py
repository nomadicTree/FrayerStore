import sqlite3
from frayerstore.models.level import Level
from frayerstore.models.level_create import LevelCreate


class LevelMapper:
    def row_to_domain(self, row: sqlite3.Row) -> Level:
        return Level(
            pk=row["id"],
            name=row["name"],
            slug=row["slug"],
        )

    def create_to_params(self, data: LevelCreate) -> tuple:
        return (data.name, data.slug)

    def from_joined_row(self, row: sqlite3.Row) -> Level:
        return Level(pk=row["level_id"], name=row["level_name"], slug=row["level_slug"])
