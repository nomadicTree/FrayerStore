import pytest
from unittest.mock import MagicMock, call, patch

from frayerstore.importer.services.generic_import_service import GenericImportService
from frayerstore.importer.exceptions import ImporterError
from frayerstore.importer.identity import ImportDecision


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.get_by_slug = MagicMock()
    repo.get_by_name = MagicMock()
    repo.create = MagicMock()
    return repo


@pytest.fixture
def mock_stage_report():
    class Report:
        def __init__(self):
            self.created = []
            self.skipped = []
            self.errors = []

        def record_created(self, obj):
            self.created.append(obj)

        def record_skipped(self, obj):
            self.skipped.append(obj)

        def record_error(self, msg):
            self.errors.append(msg)

    return Report()


@pytest.fixture
def mock_incoming():
    """
    Fake incoming object with slug + name attributes.
    """
    obj = MagicMock()
    obj.slug = "sluggy"
    obj.name = "Namey"
    return obj


@pytest.fixture
def create_factory():
    """
    Returns a simple create_factory function.
    """
    return MagicMock(side_effect=lambda inc: f"create-dto-for-{inc}")


class DummyError(ImporterError):
    pass


# ---------------------------------------------------------------------------
# Helpers for mocking resolve_identity & handle_resolution
# ---------------------------------------------------------------------------


def mock_resolution(decision, existing=None, error=None):
    """
    Build a fake IdentityResolutionResult-like object for mocking.
    """
    return MagicMock(decision=decision, existing=existing, error=error)


# ---------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------


def test_skip_path_returns_existing(
    mock_repo, create_factory, mock_incoming, mock_stage_report
):
    service = GenericImportService(
        repo=mock_repo,
        create_factory=create_factory,
        exception_type=DummyError,
    )

    existing_obj = MagicMock()

    # Mock repo lookups
    mock_repo.get_by_slug.return_value = existing_obj
    mock_repo.get_by_name.return_value = existing_obj

    # Patch resolve_identity + handle_resolution
    with (
        patch(
            "frayerstore.importer.services.generic_import_service.resolve_identity"
        ) as ri,
        patch(
            "frayerstore.importer.services.generic_import_service.handle_resolution"
        ) as hr,
    ):
        ri.return_value = mock_resolution(ImportDecision.SKIP, existing=existing_obj)
        hr.return_value = existing_obj

        result = service.import_item(mock_incoming, mock_stage_report)

    # Should return the existing item
    assert result is existing_obj

    # Should NOT call create() or record_created()
    mock_repo.create.assert_not_called()
    assert mock_stage_report.created == []

    # create_factory should NOT be called
    create_factory.assert_not_called()


def test_error_path_raises_exception(
    mock_repo, create_factory, mock_incoming, mock_stage_report
):
    service = GenericImportService(
        repo=mock_repo,
        create_factory=create_factory,
        exception_type=DummyError,
    )

    with (
        patch(
            "frayerstore.importer.services.generic_import_service.resolve_identity"
        ) as ri,
        patch(
            "frayerstore.importer.services.generic_import_service.handle_resolution"
        ) as hr,
    ):
        ri.return_value = mock_resolution(ImportDecision.ERROR, error="boom")

        # handle_resolution should raise DummyError
        hr.side_effect = DummyError("boom")

        with pytest.raises(DummyError):
            service.import_item(mock_incoming, mock_stage_report)

    # No create should run
    mock_repo.create.assert_not_called()
    create_factory.assert_not_called()


def test_create_path_creates_new_entity(
    mock_repo, create_factory, mock_incoming, mock_stage_report
):
    service = GenericImportService(
        repo=mock_repo,
        create_factory=create_factory,
        exception_type=DummyError,
    )

    created_obj = MagicMock()
    mock_repo.create.return_value = created_obj

    # Mock lookups return None (nothing exists yet)
    mock_repo.get_by_slug.return_value = None
    mock_repo.get_by_name.return_value = None

    # Patch identity to say CREATE
    with (
        patch(
            "frayerstore.importer.services.generic_import_service.resolve_identity"
        ) as ri,
        patch(
            "frayerstore.importer.services.generic_import_service.handle_resolution"
        ) as hr,
    ):
        ri.return_value = mock_resolution(ImportDecision.CREATE)
        hr.return_value = None  # meaning "go into CREATE branch"

        result = service.import_item(mock_incoming, mock_stage_report)

    # ensure we went through create path
    create_factory.assert_called_once_with(mock_incoming)
    mock_repo.create.assert_called_once_with("create-dto-for-{}".format(mock_incoming))

    # ensure stage report recorded the created object
    assert mock_stage_report.created == [created_obj]

    # final return value should be the newly created domain object
    assert result is created_obj


def test_repo_lookup_called_correctly(
    mock_repo, create_factory, mock_incoming, mock_stage_report
):
    service = GenericImportService(
        repo=mock_repo,
        create_factory=create_factory,
        exception_type=DummyError,
    )

    with (
        patch(
            "frayerstore.importer.services.generic_import_service.resolve_identity"
        ) as ri,
        patch(
            "frayerstore.importer.services.generic_import_service.handle_resolution"
        ) as hr,
    ):
        ri.return_value = mock_resolution(ImportDecision.CREATE)
        hr.return_value = None

        service.import_item(mock_incoming, mock_stage_report)

    mock_repo.get_by_slug.assert_called_once_with("sluggy")
    mock_repo.get_by_name.assert_called_once_with("Namey")


def test_handle_resolution_decides_skip_or_create(
    mock_repo, create_factory, mock_incoming, mock_stage_report
):
    """
    Ensures handle_resolution's return value truly controls CREATE vs SKIP.
    """

    service = GenericImportService(
        repo=mock_repo,
        create_factory=create_factory,
        exception_type=DummyError,
    )

    # Case A: handle_resolution returns an object → skip path
    with (
        patch(
            "frayerstore.importer.services.generic_import_service.resolve_identity"
        ) as ri,
        patch(
            "frayerstore.importer.services.generic_import_service.handle_resolution"
        ) as hr,
    ):
        ri.return_value = mock_resolution(ImportDecision.SKIP)
        hr.return_value = "EXISTING"

        result = service.import_item(mock_incoming, mock_stage_report)

        assert result == "EXISTING"
        mock_repo.create.assert_not_called()

    # Case B: handle_resolution returns None → trigger CREATE
    mock_repo.create.reset_mock()
    create_factory.reset_mock()

    with (
        patch(
            "frayerstore.importer.services.generic_import_service.resolve_identity"
        ) as ri,
        patch(
            "frayerstore.importer.services.generic_import_service.handle_resolution"
        ) as hr,
    ):
        ri.return_value = mock_resolution(ImportDecision.CREATE)
        hr.return_value = None

        mock_repo.create.return_value = "CREATED"
        result = service.import_item(mock_incoming, mock_stage_report)

        assert result == "CREATED"
        mock_repo.create.assert_called()
        assert mock_stage_report.created == ["CREATED"]
