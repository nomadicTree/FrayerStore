from __future__ import annotations
from dataclasses import dataclass, field
from frayerstore.models.domain_entity import DomainEntity
from frayerstore.models.course import Course


@dataclass(eq=False)
class Subject(DomainEntity):
    courses: list[Course] = field(default_factory=list)

    @property
    def label(self) -> str:
        return self.name
