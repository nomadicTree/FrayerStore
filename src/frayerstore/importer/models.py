from __future__ import annotations
from dataclasses import dataclass, replace
from abc import ABC, abstractmethod
import sqlite3


@dataclass(frozen=True)
class ImportItem(ABC):
    id: int | None
    name: str
    slug: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> ImportItem:
        return cls(id=row["id"], name=row["name"], slug=row["slug"])

    @classmethod
    @abstractmethod
    def from_yaml(cls, data: dict) -> ImportItem:
        pass

    @classmethod
    @abstractmethod
    def create_in_db(cls, conn: sqlite3.Row, incoming: ImportItem) -> ImportItem:
        pass

    def with_id(self, new_id: int) -> ImportItem:
        """Return a copy of this item with a new id."""
        return replace(self, id=new_id)
