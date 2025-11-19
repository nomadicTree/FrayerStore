import re
from dataclasses import dataclass
from app.core.models.course_model import Course


@dataclass(eq=False, order=False)
class Topic:
    pk: int
    code: str
    name: str
    course: Course

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Topic):
            return NotImplemented
        return self.pk == other.pk

    def __hash__(self) -> int:
        return hash(self.topic_id)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Topic):
            return NotImplemented
        return self.code < other.code

    @property
    def slug(self):
        safe_code = self.code.replace(".", "-")
        name = self.name.strip().lower()
        slug = re.sub(r"[^a-z0-9]+", "-", name)
        slug = slug.strip("-")
        return f"#{safe_code}-{slug}"

    @property
    def url(self):
        subject = self.course.subject.name.replace(" ", "+")
        course = self.course.name.replace(" ", "+")
        return f"/topic_glossary?subject={subject}&course={course}{self.slug}"

    @property
    def label(self):
        return f"{self.code}: {self.name}"
