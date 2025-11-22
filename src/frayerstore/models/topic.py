from __future__ import annotations
from dataclasses import dataclass
from frayerstore.models.domain_entity import DomainEntity
from frayerstore.models.course import Course


@dataclass(frozen=True, order=False)
class Topic(DomainEntity):
    code: str
    name: str
    slug: str
    course: Course

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Topic):
            return NotImplemented
        return self.code < other.code

    @property
    def label(self):
        return f"{self.code}: {self.name}"
