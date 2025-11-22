from frayerstore.importer.exceptions import InvalidYamlStructure
from frayerstore.importer.dto.import_level import ImportCourse

from frayerstore.importer.services.generic_import_service import GenericImportService
from frayerstore.importer.services.topic_import_coordinator import (
    TopicImportCoordinator,
)


class CourseImportCoordinator:
    def __init__(
        self,
        course_service: GenericImportService,
        topic_coordinator: TopicImportCoordinator,
    ):
        self.course_service = course_service
        self.topic_coordinator = topic_coordinator

    def import_course(self, data: dict, level_pk: int, report):
        incoming = ImportCourse.from_yaml(data, level_pk=level_pk)
        course = self.course_service.import_item(incoming, report.courses)

        topics_raw = data.get("topics", [])
        if not isinstance(topics_raw, list):
            raise InvalidYamlStructure("'topics' must be a list")

        for topic_raw in topics_raw:
            self.topic_coordinator.import_topic(topic_raw, course.pk, report)
