from dataclasses import dataclass


@dataclass(frozen=True)
class DomainEntity:
    """Base class for all domain entities with database identity."""

    pk: int

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DomainEntity):
            return NotImplemented
        return self.pk == other.pk

    def __hash__(self) -> int:
        return hash(self.pk)
