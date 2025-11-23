from typing import Protocol
from frayerstore.models.course import Course
from frayerstore.models.course_create import CourseCreate


class CourseRepository(Protocol):
    def get_by_id(self, id: int) -> Course | None:
        """Retrieve a Course by id, optionally including topics."""
        ...

    def get_by_slug(self, slug: str) -> Course | None:
        """Retrieve a Course by slug, optionally including topics."""
        ...

    def get_by_name(self, name: str) -> Course | None:
        """Retrieve a Course by name, optionally including topics."""
        ...

    def get_for_subject(
        self,
        subject_id: int,
        include_topics: bool = False,
    ) -> list[Course]:
        """Retrieve all Courses matching the given subject, optionally including topics."""
        ...

    def list_all(self, include_topics: bool = False) -> list[Course]:
        """Retrieve all Courses, optionally including topics."""
        ...

    def create(self, data: CourseCreate) -> Course:
        """Insert new row for CourseCreate."""
        ...
