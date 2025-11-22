from dataclasses import dataclass


@dataclass(frozen=True)
class Topic:
    code: str
    name: str
    slug: str
    course_pk: int
