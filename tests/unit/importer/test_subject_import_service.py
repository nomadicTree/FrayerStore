import pytest

from frayerstore.importer.services.import_services import SubjectImportService
from frayerstore.importer.dto.import_subject import ImportSubject
from frayerstore.importer.report import ImportStageReport
from frayerstore.importer.exceptions import SubjectImportError
from frayerstore.models.subject import Subject
from frayerstore.models.subject_create import SubjectCreate


# ---------------------------------------------------------------------------
# FAKE REPOSITORY
# ---------------------------------------------------------------------------


class FakeSubjectRepo:
    """
    A minimal fake repository that behaves like a real repo
    but stores data in memory.
    """

    def __init__(self):
        self.created = []
        self.by_slug = {}
        self.by_name = {}

    def get_by_slug(self, slug):
        return self.by_slug.get(slug)

    def get_by_name(self, name):
        return self.by_name.get(name)

    def create(self, candidate: SubjectCreate):
        new = Subject(
            pk=len(self.created) + 1, name=candidate.name, slug=candidate.slug
        )
        self.created.append(new)
        self.by_slug[new.slug] = new
        self.by_name[new.name] = new
        return new


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------


def make_incoming(name: str):
    """Helper: construct ImportSubject DTO."""
    from frayerstore.core.utils.slugify import slugify

    slug = slugify(name)
    return ImportSubject(name=name, slug=slug)


# ---------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------


def test_creates_subject_when_none_exists():
    repo = FakeSubjectRepo()
    service = SubjectImportService(repo)
    report = ImportStageReport("Subjects")

    incoming = make_incoming("Computing")

    result = service.import_item(incoming, report)

    # repo.create was called
    assert len(repo.created) == 1
    assert result.name == "Computing"
    assert result.slug == "computing"

    # report updated
    assert report.created == [result]
    assert report.skipped == []
    assert report.errors == []


def test_skips_when_slug_match_exists():
    repo = FakeSubjectRepo()
    service = SubjectImportService(repo)
    report = ImportStageReport("Subjects")

    # Existing subject in repo (slug matches incoming.slug)
    existing = repo.create(SubjectCreate(name="Computing", slug="computing"))

    incoming = make_incoming("Computing")

    result = service.import_subject(incoming, report)

    # Should return the existing one
    assert result is existing

    # Nothing created
    assert len(repo.created) == 1

    # Report records skip
    assert report.skipped == [existing]
    assert report.created == []
    assert report.errors == []


def test_skips_when_name_match_exists():
    repo = FakeSubjectRepo()
    service = SubjectImportService(repo)
    report = ImportStageReport("Subjects")

    # Insert with slug "computing"
    existing = repo.create(SubjectCreate(name="Computing", slug="computing"))

    # Incoming has same name -> same slug
    incoming = make_incoming("Computing")

    result = service.import_subject(incoming, report)

    assert result is existing
    assert report.skipped == [existing]
    assert report.created == []
    assert not report.errors


def test_error_when_name_conflicts_with_existing_slug():
    """
    existing_by_slug.name != incoming.name → identity error
    """
    repo = FakeSubjectRepo()
    service = SubjectImportService(repo)
    report = ImportStageReport("Subjects")

    # Existing subject: slug "computing", name "Computing"
    repo.create(SubjectCreate(name="Computing", slug="computing"))

    # Incoming with same slug but different name → conflict
    incoming = ImportSubject(name="Different Name", slug="computing")

    with pytest.raises(SubjectImportError):
        service.import_subject(incoming, report)

    assert len(report.errors) == 1
    assert report.created == []
    assert report.skipped == []


def test_error_when_slug_conflicts_with_existing_name():
    """
    existing_by_name.slug != incoming.slug → identity error
    """
    repo = FakeSubjectRepo()
    service = SubjectImportService(repo)
    report = ImportStageReport("Subjects")

    # Existing subject: name "Computing", slug "computing"
    repo.create(SubjectCreate(name="Computing", slug="computing"))

    # Incoming with same name but different slug → conflict
    incoming = ImportSubject(name="Computing", slug="different-slug")

    with pytest.raises(SubjectImportError):
        service.import_subject(incoming, report)

    assert len(report.errors) == 1
    assert report.created == []
    assert report.skipped == []


def test_create_called_with_correct_candidate():
    repo = FakeSubjectRepo()
    service = SubjectImportService(repo)
    report = ImportStageReport("Subjects")

    incoming = make_incoming("Maths")
    _ = service.import_subject(incoming, report)

    assert isinstance(repo.created[0], Subject)
    assert repo.created[0].name == "Maths"
    assert repo.created[0].slug == "maths"
    assert report.created == [repo.created[0]]
