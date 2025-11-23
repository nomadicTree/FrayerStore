import pytest

from frayerstore.db.sqlite.subject_repo_sqlite import SQLiteSubjectRepository
from frayerstore.db.sqlite.subject_mapper import SubjectMapper
from frayerstore.db.sqlite.course_repo_sqlite import SQLiteCourseRepository
from frayerstore.db.sqlite.course_mapper import CourseMapper
from frayerstore.db.sqlite.level_mapper import LevelMapper
from frayerstore.db.sqlite.topic_repo_sqlite import SQLiteTopicRepository
from frayerstore.db.sqlite.topic_mapper import TopicMapper
from frayerstore.models.subject import Subject
from frayerstore.models.subject_create import SubjectCreate
from frayerstore.models.course import Course
from frayerstore.models.topic import Topic


# ---------------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------------


@pytest.fixture
def mapper():
    return SubjectMapper()


@pytest.fixture
def level_mapper():
    return LevelMapper()


@pytest.fixture
def course_mapper(level_mapper):
    return CourseMapper(level_mapper)


@pytest.fixture
def topic_mapper():
    return TopicMapper()


@pytest.fixture
def topic_repo(schema_db, topic_mapper):
    return SQLiteTopicRepository(schema_db, topic_mapper)


@pytest.fixture
def course_repo(schema_db, course_mapper, topic_repo):
    return SQLiteCourseRepository(schema_db, course_mapper, topic_repo)


@pytest.fixture
def repo(schema_db, mapper, course_repo):
    """Repository using the in-memory DB with schema loaded."""
    return SQLiteSubjectRepository(schema_db, mapper, course_repo)


# Helper to manually insert rows for lookup tests
def insert_subject(conn, *, name, slug):
    q = """
    INSERT INTO Subjects (name, slug)
    VALUES (?, ?)
    RETURNING id, name, slug
    """
    return conn.execute(q, (name, slug)).fetchone()


def insert_level(conn, *, name="KS4", slug="ks4"):
    q = """
    INSERT INTO Levels (name, slug)
    VALUES (?, ?)
    RETURNING id, name, slug
    """
    return conn.execute(q, (name, slug)).fetchone()


def insert_course(conn, *, subject_id, level_id, name="Algorithms", slug="algorithms"):
    q = """
    INSERT INTO Courses (subject_id, level_id, name, slug)
    VALUES (?, ?, ?, ?)
    RETURNING id, subject_id, level_id, name, slug
    """
    return conn.execute(q, (subject_id, level_id, name, slug)).fetchone()


def insert_topic(conn, *, course_id, code="A1", name="Arrays", slug="arrays"):
    q = """
    INSERT INTO Topics (course_id, code, name, slug)
    VALUES (?, ?, ?, ?)
    RETURNING id, course_id, code, name, slug
    """
    return conn.execute(q, (course_id, code, name, slug)).fetchone()


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
    assert created.courses == []


def test_create_uses_mapper_to_build_params(schema_db, mapper, monkeypatch):
    repo = SQLiteSubjectRepository(schema_db, mapper, course_repo=None)

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
    assert subject.courses == []


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
    assert subject.courses == []


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
    assert subject.courses == []


def test_get_by_id_returns_none_when_missing(repo):
    assert repo.get_by_id(9999) is None


def test_get_by_id_hydrates_courses_when_requested(schema_db, repo):
    subject_row = insert_subject(schema_db, name="History", slug="history")
    level = insert_level(schema_db)
    c1 = insert_course(schema_db, subject_id=subject_row["id"], level_id=level["id"], name="Ancient", slug="ancient")
    c2 = insert_course(schema_db, subject_id=subject_row["id"], level_id=level["id"], name="Modern", slug="modern")

    subject = repo.get_by_id(subject_row["id"], include_courses=True)

    assert isinstance(subject, Subject)
    assert [c.name for c in subject.courses] == ["Ancient", "Modern"]
    assert all(isinstance(c, Course) for c in subject.courses)
    assert {c.pk for c in subject.courses} == {c1["id"], c2["id"]}


def test_get_by_id_hydrates_courses_and_topics(schema_db, repo):
    subject_row = insert_subject(schema_db, name="Computing", slug="computing")
    level = insert_level(schema_db)
    course_row = insert_course(schema_db, subject_id=subject_row["id"], level_id=level["id"])
    insert_topic(schema_db, course_id=course_row["id"], code="A1", name="Arrays", slug="arrays")
    insert_topic(schema_db, course_id=course_row["id"], code="A2", name="Loops", slug="loops")

    subject = repo.get_by_id(subject_row["id"], include_courses=True, include_topics=True)

    assert isinstance(subject, Subject)
    assert len(subject.courses) == 1
    course = subject.courses[0]
    assert isinstance(course, Course)
    assert [t.code for t in course.topics] == ["A1", "A2"]
    assert all(isinstance(t, Topic) for t in course.topics)


def test_list_all_orders_by_name(schema_db, repo):
    insert_subject(schema_db, name="Zoology", slug="zoo")
    insert_subject(schema_db, name="Biology", slug="bio")

    subjects = repo.list_all()

    assert [s.name for s in subjects] == ["Biology", "Zoology"]
