from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class DomainEntity:
    """Base class for all domain entities with database identity."""

    pk: Optional[int] = None

    def has_identity(self) -> bool:
        return self.pk is not None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DomainEntity):
            return NotImplemented

        if self.has_identity() and other.has_identity():
            return self.pk == other.pk

        return False

    def __hash__(self) -> int:
        if self.has_identity():
            return hash(self.pk)
        else:
            # Entities without pk are not hashable
            return id(self)
