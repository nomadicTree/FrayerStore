from app.core.models.subject_model import Subject
from app.core.models.level_model import Level


class Course:
    def __init__(self, course_id: int, name: str, subject: Subject, level: Level):
        self.course_id = course_id
        self.name = name
        self.subject = subject
        self.level = level

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Course):
            return NotImplemented
        return self.course_id == other.course_id

    def __hash__(self) -> int:
        return hash(self.course_id)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Course):
            return NotImplemented
        if self.level != other.level:
            return self.level < other.level

        return self.name.lower() < other.name.lower()

    @property
    def pk(self):
        return self.course_id
