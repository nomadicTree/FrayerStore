from app.core.models.course_model import Course
import re


class Topic:
    def __init__(self, topic_id: int, code: str, name: str, course: Course):
        self.topic_id = topic_id
        self.code = code
        self.name = name
        self.course = course

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Topic):
            return NotImplemented
        return self.topic_id == other.topic_id

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

    @property
    def pk(self):
        return self.topic_id
