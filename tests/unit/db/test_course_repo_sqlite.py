import pytest

from frayerstore.db.sqlite.course_repo_sqlite import SQLiteCourseRepository
from frayerstore.db.sqlite.course_mapper import CourseMapper
from frayerstore.db.sqlite.level_mapper import LevelMapper
from frayerstore.db.sqlite.topic_repo_sqlite import SQLiteTopicRepository
from frayerstore.db.sqlite.topic_mapper import TopicMapper
from frayerstore.models.course import Course
from frayerstore.models.course_create import CourseCreate
from frayerstore.models.topic import Topic
from frayerstore.models.topic_create import TopicCreate


# ---------------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------------


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
def repo(schema_db, course_mapper, topic_repo):
    return SQLiteCourseRepository(schema_db, course_mapper, topic_repo)


# Helpers


def insert_subject(conn, name="Computing", slug="computing"):
    return conn.execute(
        "INSERT INTO Subjects (name, slug) VALUES (?, ?) RETURNING id, name, slug",
        (name, slug),
    ).fetchone()


def insert_level(conn, name="KS4", slug="ks4"):
    return conn.execute(
        "INSERT INTO Levels (name, slug) VALUES (?, ?) RETURNING id, name, slug",
        (name, slug),
    ).fetchone()


def insert_course(conn, *, subject_id, level_id, name="Algorithms", slug="algorithms"):
    return conn.execute(
        """
        INSERT INTO Courses (subject_id, level_id, name, slug)
        VALUES (?, ?, ?, ?)
        RETURNING id, subject_id, level_id, name, slug
        """,
        (subject_id, level_id, name, slug),
    ).fetchone()


def insert_topic(
    conn,
    *,
    course_id,
    code="A1",
    name="Arrays",
    slug="arrays",
):
    return conn.execute(
        """
        INSERT INTO Topics (course_id, code, name, slug)
        VALUES (?, ?, ?, ?)
        RETURNING id, course_id, code, name, slug
        """,
        (course_id, code, name, slug),
    ).fetchone()


# ---------------------------------------------------------------------------
# CREATE TESTS
# ---------------------------------------------------------------------------


def test_create_inserts_row_and_returns_domain(schema_db, repo):
    subject = insert_subject(schema_db)
    level = insert_level(schema_db)
    data = CourseCreate(
        subject_pk=subject["id"],
        level_pk=level["id"],
        name="Algorithms",
        slug="algorithms",
    )

    created = repo.create(data)

    row = schema_db.execute("SELECT * FROM Courses WHERE slug='algorithms'").fetchone()
    assert row is not None
    assert row["name"] == "Algorithms"
    assert row["subject_id"] == subject["id"]
    assert row["level_id"] == level["id"]

    assert isinstance(created, Course)
    assert created.pk == row["id"]
    assert created.subject_pk == subject["id"]
    assert created.level.pk == level["id"]
    assert created.level.slug == "ks4"
    assert created.topics == []


def test_create_uses_mapper_to_build_params(schema_db, course_mapper, topic_repo, monkeypatch):
    subject = insert_subject(schema_db)
    level = insert_level(schema_db)
    repo = SQLiteCourseRepository(schema_db, course_mapper, topic_repo)

    called = {}

    def fake_params(data):
        called["used"] = True
        return (subject["id"], level["id"], "X", "x")

    monkeypatch.setattr(course_mapper, "create_to_params", fake_params)

    repo.create(CourseCreate(name="X", slug="x", subject_pk=subject["id"], level_pk=level["id"]))

    assert called.get("used") is True


# ---------------------------------------------------------------------------
# LOOKUP TESTS
# ---------------------------------------------------------------------------


def setup_course(conn, *, name="Algorithms", slug="algorithms"):
    subject = insert_subject(conn)
    level = insert_level(conn)
    return insert_course(conn, subject_id=subject["id"], level_id=level["id"], name=name, slug=slug)


def test_get_by_slug_returns_course(repo, schema_db):
    row = setup_course(schema_db)

    course = repo.get_by_slug(row["slug"])

    assert isinstance(course, Course)
    assert course.pk == row["id"]
    assert course.name == row["name"]
    assert course.subject_pk == row["subject_id"]
    assert course.level.pk == row["level_id"]
    assert course.topics == []


def test_get_by_slug_returns_none_when_missing(repo):
    assert repo.get_by_slug("missing") is None


def test_get_by_name_returns_course(repo, schema_db):
    row = setup_course(schema_db)

    course = repo.get_by_name(row["name"])

    assert isinstance(course, Course)
    assert course.slug == row["slug"]
    assert course.level.name is not None


def test_get_by_name_returns_none_when_missing(repo):
    assert repo.get_by_name("Imaginary Course") is None


def test_get_by_id_returns_course(repo, schema_db):
    row = setup_course(schema_db)

    course = repo.get_by_id(row["id"])

    assert isinstance(course, Course)
    assert course.pk == row["id"]
    assert course.name == row["name"]
    assert course.level.slug == "ks4"


def test_get_by_id_returns_none_when_missing(repo):
    assert repo.get_by_id(9999) is None


def test_get_for_subject_returns_courses_sorted_by_name(repo, schema_db):
    subject = insert_subject(schema_db)
    level = insert_level(schema_db)
    insert_course(schema_db, subject_id=subject["id"], level_id=level["id"], name="Zoology", slug="z")
    insert_course(schema_db, subject_id=subject["id"], level_id=level["id"], name="Algebra", slug="a")

    courses = repo.get_for_subject(subject["id"])

    assert [c.name for c in courses] == ["Algebra", "Zoology"]


def test_get_by_id_with_topics_includes_topics_when_requested(repo, schema_db, topic_repo):
    row = setup_course(schema_db)
    insert_topic(schema_db, course_id=row["id"], code="A1", name="Arrays", slug="arrays")
    insert_topic(schema_db, course_id=row["id"], code="A2", name="Loops", slug="loops")

    course = repo.get_by_id(row["id"], include_topics=True)

    assert isinstance(course, Course)
    assert len(course.topics) == 2
    assert all(isinstance(t, Topic) for t in course.topics)
    assert [t.code for t in course.topics] == ["A1", "A2"]
