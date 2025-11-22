import pytest

from frayerstore.importer.dto.import_subject import ImportSubject
from frayerstore.importer.exceptions import SubjectImportError
from frayerstore.importer.report import ImportReport
from frayerstore.importer.yaml_utils import load_yaml


def make_subject_service(conn):
    from frayerstore.db.sqlite.subject_mapper import SubjectMapper
    from frayerstore.db.sqlite.subject_repo_sqlite import SQLiteSubjectRepository
    from frayerstore.importer.services.subject_import_service import (
        SubjectImportService,
    )

    mapper = SubjectMapper()
    repo = SQLiteSubjectRepository(conn, mapper)
    return SubjectImportService(repo)


def run_import(conn, yaml_path, report):
    """Helper: load YAML → DTO → import via service."""
    service = make_subject_service(conn)
    data = load_yaml(yaml_path)
    incoming = ImportSubject.from_yaml(data)
    return service.import_subject(incoming, report.subjects)


# ---------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------


def test_import_single_subject(schema_db, subjects_path):
    subject_yaml = subjects_path / "subjects.yaml"
    report = ImportReport()

    run_import(schema_db, subject_yaml, report)

    row = schema_db.execute(
        "SELECT * FROM Subjects WHERE name = 'Computing'"
    ).fetchone()

    assert row is not None
    assert row["name"] == "Computing"
    assert row["slug"] == "computing"

    count = schema_db.execute("SELECT COUNT(*) FROM Subjects").fetchone()[0]
    assert count == 1

    assert len(report.subjects.created) == 1
    assert not report.subjects.skipped
    assert not report.subjects.errors


def test_import_multiple_subjects(schema_db, tmp_path):
    a = tmp_path / "a.yaml"
    b = tmp_path / "b.yaml"
    report = ImportReport()

    a.write_text("name: Computing")
    b.write_text("name: Maths")

    run_import(schema_db, a, report)
    run_import(schema_db, b, report)

    rows = schema_db.execute("SELECT * FROM Subjects").fetchall()
    assert len(rows) == 2

    names = {r["name"] for r in rows}
    assert names == {"Computing", "Maths"}

    assert len(report.subjects.created) == 2
    assert not report.subjects.skipped
    assert not report.subjects.errors


def test_subject_name_collision(schema_db, tmp_path):
    a = tmp_path / "a.yaml"
    b = tmp_path / "b.yaml"
    report = ImportReport()

    a.write_text("name: Computing")
    b.write_text("name: Computing")

    run_import(schema_db, a, report)
    run_import(schema_db, b, report)

    rows = schema_db.execute("SELECT * FROM Subjects").fetchall()
    assert len(rows) == 1

    assert len(report.subjects.created) == 1
    assert len(report.subjects.skipped) == 1
    assert not report.subjects.errors


def test_subject_slug_is_derived(schema_db, tmp_path):
    yaml = tmp_path / "sub.yaml"
    yaml.write_text("name: Computer Science")

    report = ImportReport()
    run_import(schema_db, yaml, report)

    row = schema_db.execute("SELECT slug FROM Subjects").fetchone()
    assert row["slug"] == "computer-science"


@pytest.mark.parametrize(
    "name, expected_slug",
    [
        ("Computing", "computing"),
        ("Computer Science", "computer-science"),
        ("  Data   Structures ", "data-structures"),
        ("AI & ML", "ai-ml"),
        ("C++ Programming", "c-programming"),
    ],
)
def test_slug_derivation_rules(schema_db, tmp_path, name, expected_slug):
    file = tmp_path / "sub.yaml"
    file.write_text(f"name: {name}")

    report = ImportReport()
    run_import(schema_db, file, report)

    slug = schema_db.execute("SELECT slug FROM Subjects").fetchone()["slug"]
    assert slug == expected_slug


def test_slug_collision(schema_db, tmp_path):
    a = tmp_path / "a.yaml"
    b = tmp_path / "b.yaml"
    report = ImportReport()

    a.write_text("name: Class")
    b.write_text("name: class")  # same slug

    run_import(schema_db, a, report)

    with pytest.raises(SubjectImportError):
        run_import(schema_db, b, report)

    rows = schema_db.execute("SELECT * FROM Subjects").fetchall()
    assert len(rows) == 1

    assert len(report.subjects.created) == 1
    assert not report.subjects.skipped
    assert len(report.subjects.errors) == 1
