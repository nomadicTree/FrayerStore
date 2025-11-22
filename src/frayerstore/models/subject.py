from dataclasses import dataclass
from .domain_entity import DomainEntity


@dataclass(frozen=True)
class Subject(DomainEntity):
    name: str
    slug: str

    @property
    def label(self):
        return self.name
