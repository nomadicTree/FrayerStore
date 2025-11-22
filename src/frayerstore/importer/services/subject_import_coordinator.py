from frayerstore.importer.exceptions import InvalidYamlStructure
from frayerstore.importer.dto.import_subject import ImportSubject
from frayerstore.importer.services.generic_import_service import GenericImportService
from frayerstore.importer.services.level_import_coordinator import (
    LevelImportCoordinator,
)


class SubjectImportCoordinator:
    def __init__(
        self,
        subject_service: GenericImportService,
        level_coordinator: LevelImportCoordinator,
    ):
        self.subject_service = subject_service
        self.level_coordinator = level_coordinator

    def import_from_yaml(self, data: dict, report):
        # 1. Parse subject DTO
        incoming = ImportSubject.from_yaml(data)
        subject = self.subject_service.import_item(incoming, report.subjects)

        # 2. Import levels
        levels_raw = data.get("levels", [])
        if not isinstance(levels_raw, list):
            raise InvalidYamlStructure("'levels' must be a list")

        for level_raw in levels_raw:
            self.level_coordinator.import_level(level_raw, subject.pk, report)
