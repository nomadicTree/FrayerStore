import pytest

from frayerstore.db.sqlite.subject_repo_sqlite import SQLiteSubjectRepository
from frayerstore.db.sqlite.subject_mapper import SubjectMapper
from frayerstore.models.subject import Subject
from frayerstore.models.subject_create import SubjectCreate


# ---------------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------------


@pytest.fixture
def mapper():
    return SubjectMapper()


@pytest.fixture
def repo(schema_db, mapper):
    """Repository using the in-memory DB with schema loaded."""
    return SQLiteSubjectRepository(schema_db, mapper)


# Helper to manually insert rows for lookup tests
def insert_subject(conn, *, name, slug):
    q = """
    INSERT INTO Subjects (name, slug)
    VALUES (?, ?)
    RETURNING id, name, slug
    """
    return conn.execute(q, (name, slug)).fetchone()


# ---------------------------------------------------------------------------
# CREATE TESTS
# ---------------------------------------------------------------------------


def test_create_inserts_row_and_returns_domain(schema_db, repo):
    data = SubjectCreate(name="Computing", slug="computing")

    created = repo.create(data)

    # Verify row is inserted
    row = schema_db.execute("SELECT * FROM Subjects WHERE slug='computing'").fetchone()
    assert row is not None
    assert row["name"] == "Computing"

    # Verify returned domain object
    assert isinstance(created, Subject)
    assert created.slug == "computing"
    assert created.pk == row["id"]


def test_create_uses_mapper_to_build_params(schema_db, mapper, monkeypatch):
    repo = SQLiteSubjectRepository(schema_db, mapper)

    called = {}

    def fake_params(data):
        called["used"] = True
        return ("A", "a")  # values do not matter

    monkeypatch.setattr(mapper, "create_to_params", fake_params)

    repo.create(SubjectCreate(name="X", slug="x"))
    assert called.get("used", False) is True


# ---------------------------------------------------------------------------
# GET BY SLUG TESTS
# ---------------------------------------------------------------------------


def test_get_by_slug_returns_subject(schema_db, repo):
    row = insert_subject(schema_db, name="Computing", slug="computing")

    subject = repo.get_by_slug("computing")

    assert isinstance(subject, Subject)
    assert subject.pk == row["id"]
    assert subject.name == "Computing"


def test_get_by_slug_returns_none_when_missing(repo):
    assert repo.get_by_slug("nope") is None


# ---------------------------------------------------------------------------
# GET BY NAME TESTS
# ---------------------------------------------------------------------------


def test_get_by_name_returns_subject(schema_db, repo):
    row = insert_subject(schema_db, name="Maths", slug="maths")

    subject = repo.get_by_name("Maths")

    assert isinstance(subject, Subject)
    assert subject.pk == row["id"]
    assert subject.slug == "maths"


def test_get_by_name_returns_none_when_missing(repo):
    assert repo.get_by_name("Imaginary Subject") is None


# ---------------------------------------------------------------------------
# GET BY ID TESTS
# ---------------------------------------------------------------------------


def test_get_by_id_returns_subject(schema_db, repo):
    row = insert_subject(schema_db, name="History", slug="history")

    subject = repo.get_by_id(row["id"])

    assert isinstance(subject, Subject)
    assert subject.pk == row["id"]
    assert subject.name == "History"


def test_get_by_id_returns_none_when_missing(repo):
    assert repo.get_by_id(9999) is None
