from dataclasses import dataclass


@dataclass(eq=False)
class Subject:
    pk: int
    name: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Subject):
            return NotImplemented
        return self.pk == other.pk

    def __hash__(self) -> int:
        return hash(self.pk)

    @property
    def pk(self):
        return self.pk
