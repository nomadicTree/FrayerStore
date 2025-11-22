import pytest
from frayerstore.importer.exceptions import InvalidYamlStructure
from frayerstore.importer.services.subject_import_coordinator import (
    SubjectImportCoordinator,
)
# --- fakes -------------------------------------------------------------


class FakeSubject:
    def __init__(self, pk):
        self.pk = pk


class FakeSubjectService:
    def __init__(self):
        self.calls = []

    def import_item(self, incoming, stage):
        self.calls.append(("import_subject", incoming, stage))
        return FakeSubject(pk=111)


class FakeLevelCoordinator:
    def __init__(self):
        self.calls = []

    def import_level(self, data, subject_pk, report):
        self.calls.append((data, subject_pk, report))


# --- coordinator under test -------------------------------------------


# --- tests -------------------------------------------------------------


def test_subject_coordinator_imports_subject_and_levels(fake_report):
    service = FakeSubjectService()
    level_co = FakeLevelCoordinator()

    co = SubjectImportCoordinator(service, level_co)

    data = {
        "name": "Computing",
        "levels": [
            {"name": "KS4"},
            {"name": "KS5"},
        ],
    }

    co.import_subject(data, fake_report)

    # correct call to subject importer
    assert len(service.calls) == 1
    assert service.calls[0][0] == "import_subject"

    # correct number of level imports
    assert len(level_co.calls) == 2
    # correct PK passed down from subject importer
    assert level_co.calls[0][1] == 111


def test_subject_coordinator_rejects_non_list_levels(fake_report):
    service = FakeSubjectService()
    level_co = FakeLevelCoordinator()
    co = SubjectImportCoordinator(service, level_co)

    data = {"name": "Computing", "levels": "not-a-list"}

    with pytest.raises(InvalidYamlStructure):
        co.import_subject(data, fake_report)
