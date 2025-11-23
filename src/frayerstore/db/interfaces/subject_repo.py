from typing import Protocol
from frayerstore.models.subject import Subject
from frayerstore.models.subject_create import SubjectCreate


class SubjectRepository(Protocol):
    def get_by_id(self, id: int) -> Subject | None:
        """Retrieve a Subject by id, optionally including courses and topics."""
        ...

    def get_by_slug(self, slug: str) -> Subject | None:
        """Retrieve a Subject by slug, optionally including courses and topics."""
        ...

    def get_by_name(self, name: str) -> Subject | None:
        """Retrieve a Subject by name, optionally including courses and topics."""
        ...

    def list_all(
        self, include_courses: bool = False, include_topics: bool = False
    ) -> list[Subject] | None:
        """Retrieve all Subjects, optionally including courses and topics."""
        ...

    def create(self, data: SubjectCreate) -> Subject:
        """Insert new row for SubjectCreate."""
        ...
