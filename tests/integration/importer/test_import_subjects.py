import pytest
from pathlib import Path

from frayerstore.importer.import_items import import_subjects_from_file
from frayerstore.importer.report import ImportReport
from frayerstore.importer.exceptions import SubjectImportError

from frayerstore.db.sqlite.subject_mapper import SubjectMapper
from frayerstore.db.sqlite.subject_repo_sqlite import SQLiteSubjectRepository
from frayerstore.importer.services.import_services import SubjectImportService


# ---------------------------------------------------------------------------
# FIXTURES / HELPERS
# ---------------------------------------------------------------------------


def make_import_service(conn):
    """
    Build the SubjectImportService wired to SQLite.
    """
    mapper = SubjectMapper()
    repo = SQLiteSubjectRepository(conn, mapper)
    return SubjectImportService(repo)


def write_single_subject_yaml(path: Path, name: str):
    path.write_text(f"subjects:\n  - name: {name}\n")


def write_two_subject_yaml(path: Path, name1: str, name2: str):
    path.write_text(f"subjects:\n  - name: {name1}\n  - name: {name2}\n")


# ---------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------


def test_import_single_subject(schema_db, tmp_path):
    file = tmp_path / "subjects.yaml"
    write_single_subject_yaml(file, "Computing")

    report = ImportReport()
    import_service = make_import_service(schema_db)

    import_subjects_from_file(file, import_service, report)

    row = schema_db.execute(
        "SELECT * FROM Subjects WHERE name = 'Computing'"
    ).fetchone()

    assert row is not None
    assert row["name"] == "Computing"
    assert row["slug"] == "computing"

    assert schema_db.execute("SELECT COUNT(*) FROM Subjects").fetchone()[0] == 1

    assert len(report.subjects.created) == 1
    assert not report.subjects.skipped
    assert not report.subjects.errors


def test_import_multiple_subjects(schema_db, tmp_path):
    file = tmp_path / "subjects.yaml"
    write_two_subject_yaml(file, "Computing", "Maths")

    report = ImportReport()
    import_service = make_import_service(schema_db)

    import_subjects_from_file(file, import_service, report)

    rows = schema_db.execute("SELECT * FROM Subjects").fetchall()
    assert len(rows) == 2

    assert {r["name"] for r in rows} == {"Computing", "Maths"}

    assert len(report.subjects.created) == 2
    assert not report.subjects.skipped
    assert not report.subjects.errors


def test_subject_name_collision(schema_db, tmp_path):
    file = tmp_path / "subjects.yaml"
    write_two_subject_yaml(file, "Computing", "Computing")

    report = ImportReport()
    import_service = make_import_service(schema_db)

    import_subjects_from_file(file, import_service, report)

    rows = schema_db.execute("SELECT * FROM Subjects").fetchall()
    assert len(rows) == 1

    assert len(report.subjects.created) == 1
    assert len(report.subjects.skipped) == 1
    assert not report.subjects.errors


def test_subject_slug_is_derived(schema_db, tmp_path):
    file = tmp_path / "subjects.yaml"
    write_single_subject_yaml(file, "Computer Science")

    report = ImportReport()
    import_service = make_import_service(schema_db)

    import_subjects_from_file(file, import_service, report)

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
    file = tmp_path / "subjects.yaml"
    write_single_subject_yaml(file, name)

    report = ImportReport()
    import_service = make_import_service(schema_db)

    import_subjects_from_file(file, import_service, report)

    slug = schema_db.execute("SELECT slug FROM Subjects").fetchone()["slug"]
    assert slug == expected_slug


def test_slug_collision(schema_db, tmp_path):
    file = tmp_path / "subjects.yaml"
    write_two_subject_yaml(file, "Class", "class")  # same slug

    report = ImportReport()
    import_service = make_import_service(schema_db)

    with pytest.raises(SubjectImportError):
        import_subjects_from_file(file, import_service, report)

    rows = schema_db.execute("SELECT * FROM Subjects").fetchall()

    assert len(rows) == 1
    assert len(report.subjects.created) == 1
    assert not report.subjects.skipped
    assert len(report.subjects.errors) == 1
