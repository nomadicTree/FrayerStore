from dataclasses import dataclass


@dataclass(eq=False, order=False)
class Level:
    pk: int
    name: str
    description: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Level):
            return NotImplemented
        return self.pk == other.pk

    def __hash__(self) -> int:
        return hash(self.pk)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Level):
            return NotImplemented
        return self.name < other.name
