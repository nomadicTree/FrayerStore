from typing import Protocol
from frayerstore.models.level import Level
from frayerstore.models.level_create import LevelCreate


class LevelRepository(Protocol):
    def get_by_id(self, id: int) -> Level | None:
        """Retrieve a Level by id."""
        ...

    def get_by_slug(self, slug: str) -> Level | None:
        """Retrieve a Level by slug."""
        ...

    def get_by_name(self, name: str) -> Level | None:
        """Retrieve a Level by name."""
        ...

    def list_all(self) -> list[Level]:
        """Retrieve all Levels."""
        ...

    def create(self, data: LevelCreate) -> Level:
        """Insert new row for LevelCreate."""
        ...
