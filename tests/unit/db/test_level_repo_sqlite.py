import pytest

from frayerstore.db.sqlite.level_repo_sqlite import SQLiteLevelRepository
from frayerstore.db.sqlite.level_mapper import LevelMapper
from frayerstore.models.level import Level
from frayerstore.models.level_create import LevelCreate


# ---------------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------------


@pytest.fixture
def conn(schema_db):
    """
    Uses your existing schema_db fixture (with Levels table created).
    """
    return schema_db


@pytest.fixture
def mapper():
    return LevelMapper()


@pytest.fixture
def repo(conn, mapper):
    return SQLiteLevelRepository(conn, mapper)


# Helper: insert a row manually for testing lookups
def insert_row(conn, *, name, slug, category, number):
    q = """
    INSERT INTO Levels (name, slug, category, number)
    VALUES (?, ?, ?, ?)
    RETURNING id, name, slug, category, number
    """
    return conn.execute(q, (name, slug, category, number)).fetchone()


# ---------------------------------------------------------------------------
# TESTS FOR CREATE()
# ---------------------------------------------------------------------------


def test_create_inserts_row_and_returns_domain(conn, repo, mapper):
    data = LevelCreate(
        name="Key Stage 4",
        slug="ks4",
        category="Key Stage",
        number="4",
    )

    created = repo.create(data)

    # Check row exists in DB
    row = conn.execute("SELECT * FROM Levels WHERE slug='ks4'").fetchone()
    assert row is not None
    assert row["name"] == "Key Stage 4"

    # Check mapper returned a Level instance
    assert isinstance(created, Level)
    assert created.slug == "ks4"
    assert created.pk == row["id"]


def test_create_uses_mapper_to_generate_params(repo, mapper, conn, monkeypatch):
    """
    Verify that create_to_params() is actually used.
    """
    called = {}

    def fake_params(data):
        called["params"] = True
        return ("A", "a", "Cat", "1")

    monkeypatch.setattr(mapper, "create_to_params", fake_params)

    data = LevelCreate(name="X", slug="x", category="C", number="1")
    repo.create(data)

    assert called.get("params", False) is True


# ---------------------------------------------------------------------------
# TESTS FOR get_by_slug()
# ---------------------------------------------------------------------------


def test_get_by_slug_finds_row(repo, conn):
    row = insert_row(
        conn,
        name="Key Stage 4",
        slug="ks4",
        category="Key Stage",
        number="4",
    )

    level = repo.get_by_slug("ks4")
    assert isinstance(level, Level)
    assert level.pk == row["id"]
    assert level.slug == "ks4"


def test_get_by_slug_returns_none_if_not_found(repo):
    assert repo.get_by_slug("missing") is None


# ---------------------------------------------------------------------------
# TESTS FOR get_by_name()
# ---------------------------------------------------------------------------


def test_get_by_name_finds_row(repo, conn):
    row = insert_row(
        conn,
        name="Key Stage 5",
        slug="ks5",
        category="Key Stage",
        number="5",
    )

    level = repo.get_by_name("Key Stage 5")
    assert isinstance(level, Level)
    assert level.pk == row["id"]
    assert level.name == "Key Stage 5"


def test_get_by_name_returns_none_if_not_found(repo):
    assert repo.get_by_name("Nope") is None


# ---------------------------------------------------------------------------
# TESTS FOR get_by_id()
# ---------------------------------------------------------------------------


def test_get_by_id_finds_row(repo, conn):
    row = insert_row(
        conn,
        name="Year 12",
        slug="y12",
        category="Year",
        number="12",
    )

    level = repo.get_by_id(row["id"])
    assert isinstance(level, Level)
    assert level.pk == row["id"]
    assert level.slug == "y12"


def test_get_by_id_returns_none_if_not_found(repo):
    assert repo.get_by_id(9999) is None
