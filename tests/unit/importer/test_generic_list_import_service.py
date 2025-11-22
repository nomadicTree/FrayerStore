import pytest
from unittest.mock import MagicMock, call

from frayerstore.importer.services.generic_list_import_service import (
    GenericListImportService,
)


# ---------------------------------------------------------------------------
# Fixtures for mocking the importable classes and services
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_import_item_cls():
    """
    A fake ImportItem class with a from_yaml() classmethod.
    We mock it so no real ImportItem subclasses are needed.
    """
    cls = MagicMock()
    cls.from_yaml = MagicMock(side_effect=lambda raw: f"parsed-{raw['id']}")
    return cls


@pytest.fixture
def mock_import_service():
    """
    Pretend SubjectImportService / LevelImportService.
    It just needs an import_item() method.
    """
    service = MagicMock()
    service.import_item = MagicMock()
    return service


@pytest.fixture
def mock_report():
    """
    Mimics ImportReport with nested stage reports.
    Only the selected stage_report needs a record_xxx() interface,
    but import_item only receives stage_report, so this is simple.
    """

    class StageReport:
        pass

    class Report:
        def __init__(self):
            self.subjects = StageReport()
            self.levels = StageReport()

    return Report()


# ---------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------


def test_import_many_calls_from_yaml_and_import_item(
    mock_import_item_cls, mock_import_service, mock_report
):
    # Prepare a generic list importer
    importer = GenericListImportService(
        import_item_cls=mock_import_item_cls,
        import_service=mock_import_service,
        stage_selector=lambda r: r.subjects,
    )

    # Fake YAML data list
    data_list = [{"id": 1}, {"id": 2}, {"id": 3}]

    importer.import_many(data_list, mock_report)

    # from_yaml should be called ONCE per raw item
    assert mock_import_item_cls.from_yaml.call_count == 3

    mock_import_item_cls.from_yaml.assert_has_calls(
        [
            call({"id": 1}),
            call({"id": 2}),
            call({"id": 3}),
        ]
    )

    # import_service.import_item() should also be called once per parsed item
    assert mock_import_service.import_item.call_count == 3

    mock_import_service.import_item.assert_has_calls(
        [
            call("parsed-1", mock_report.subjects),
            call("parsed-2", mock_report.subjects),
            call("parsed-3", mock_report.subjects),
        ]
    )


def test_correct_stage_report_selected(
    mock_import_item_cls, mock_import_service, mock_report
):
    importer = GenericListImportService(
        import_item_cls=mock_import_item_cls,
        import_service=mock_import_service,
        stage_selector=lambda r: r.levels,
    )

    importer.import_many([{"id": 10}], mock_report)

    # Ensure the right stage report was passed to import_item()
    mock_import_service.import_item.assert_called_once_with(
        "parsed-10", mock_report.levels
    )


def test_empty_list_does_nothing(
    mock_import_item_cls, mock_import_service, mock_report
):
    importer = GenericListImportService(
        import_item_cls=mock_import_item_cls,
        import_service=mock_import_service,
        stage_selector=lambda r: r.subjects,
    )

    importer.import_many([], mock_report)

    mock_import_item_cls.from_yaml.assert_not_called()
    mock_import_service.import_item.assert_not_called()


def test_importer_is_configurable_per_entity(mock_import_item_cls, mock_import_service):
    # separate fake stage reports for clarity
    class Report:
        subjects = "SUBJECT_STAGE"
        levels = "LEVEL_STAGE"

    report = Report()

    # subject importer
    subject_importer = GenericListImportService(
        import_item_cls=mock_import_item_cls,
        import_service=mock_import_service,
        stage_selector=lambda r: r.subjects,
    )

    subject_importer.import_many([{"id": 1}], report)

    mock_import_service.import_item.assert_called_with("parsed-1", "SUBJECT_STAGE")

    mock_import_service.import_item.reset_mock()

    # level importer
    level_importer = GenericListImportService(
        import_item_cls=mock_import_item_cls,
        import_service=mock_import_service,
        stage_selector=lambda r: r.levels,
    )

    level_importer.import_many([{"id": 2}], report)

    mock_import_service.import_item.assert_called_with("parsed-2", "LEVEL_STAGE")
