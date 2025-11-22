from dataclasses import dataclass


@dataclass(frozen=True)
class SubjectCreate:
    name: str
    slug: str
