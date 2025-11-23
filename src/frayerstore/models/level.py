from __future__ import annotations
from dataclasses import dataclass
from frayerstore.models.domain_entity import DomainEntity


@dataclass(eq=False)
class Level(DomainEntity):
    name: str
    slug: str
