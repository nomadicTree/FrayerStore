from __future__ import annotations
from dataclasses import dataclass
from frayerstore.models.domain_entity import DomainEntity


@dataclass(frozen=True)
class Level(DomainEntity):
    # Canonical identity attributes
    name: str
    slug: str

    # Component attributes
    category: str
    number: str

    @property
    def label(self):
        return self.name  # alias

    @property
    def short_label(self) -> str:
        """Return abbreviated label, e.g. "KS4"."""
        return self.slug.upper()
