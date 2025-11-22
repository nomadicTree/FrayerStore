import pytest

from frayerstore.db.sqlite.subject_mapper import SubjectMapper
from frayerstore.models.subject import Subject
from frayerstore.models.subject_create import SubjectCreate


def make_row(id=1, name="Computing", slug="computing"):
    """
    Creates a dict-like object behaving like sqlite3.Row for testing.
    """
    return {"id": id, "name": name, "slug": slug}


@pytest.fixture
def mapper():
    return SubjectMapper()


# ---------------------------------------------------------------------------
# row_to_domain
# ---------------------------------------------------------------------------


def test_row_to_domain_returns_subject(mapper):
    row = make_row(5, "Maths", "maths")
    subject = mapper.row_to_domain(row)

    assert isinstance(subject, Subject)
    assert subject.pk == 5
    assert subject.name == "Maths"
    assert subject.slug == "maths"


def test_row_to_domain_uses_exact_fields(mapper):
    """Ensures mapper doesn't ignore or mis-map fields."""
    row = make_row(id=10, name="History", slug="history")
    subject = mapper.row_to_domain(row)

    assert subject.pk == 10
    assert subject.name == "History"
    assert subject.slug == "history"


# ---------------------------------------------------------------------------
# create_to_params
# ---------------------------------------------------------------------------


def test_create_to_params_returns_tuple_in_correct_order(mapper):
    data = SubjectCreate(name="Physics", slug="physics")
    params = mapper.create_to_params(data)

    assert params == ("Physics", "physics")


def test_create_to_params_works_with_various_inputs(mapper):
    data = SubjectCreate(name="   Biology  ", slug="bio")
    params = mapper.create_to_params(data)

    assert params == ("   Biology  ", "bio")  # trimming happens in DTO, not mapper
