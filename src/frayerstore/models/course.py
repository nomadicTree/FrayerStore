from __future__ import annotations
from dataclasses import dataclass, field
from frayerstore.models.domain_entity import DomainEntity
from frayerstore.models.level import Level
from frayerstore.models.topic import Topic


@dataclass(eq=False, order=False)
class Course(DomainEntity):
    subject_pk: int
    level: Level
    topics: list[Topic] = field(default_factory=list)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Course):
            return NotImplemented
        if self.level != other.level:
            return self.level < other.level

        return self.name.lower() < other.name.lower()

    @property
    def label(self) -> str:
        return self.name
