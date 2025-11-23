from __future__ import annotations
from dataclasses import dataclass
from frayerstore.models.domain_entity import DomainEntity


@dataclass(eq=False)
class Level(DomainEntity):
    name: str
    slug: str

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Level):
            return NotImplemented
        self_name = self.name.lower()
        other_name = other.name.lower()
        if self_name != other_name:
            return self_name < other_name
        return self.pk < other.pk
