import sqlite3
import pytest

from frayerstore.db.sqlite.level_mapper import LevelMapper
from frayerstore.models.level import Level
from frayerstore.models.level_create import LevelCreate


def make_row(
    id=1,
    name="Key Stage 4",
    slug="ks4",
    category="Key Stage",
    number="4",
):
    return {
        "id": id,
        "name": name,
        "slug": slug,
        "category": category,
        "number": number,
    }


@pytest.fixture
def mapper():
    return LevelMapper()


# ---------------------------------------------------------------------------
# row_to_domain
# ---------------------------------------------------------------------------


def test_row_to_domain_builds_level(mapper):
    row = make_row(id=7, name="Year 12", slug="y12", category="Year", number="12")
    level = mapper.row_to_domain(row)

    assert isinstance(level, Level)
    assert level.pk == 7
    assert level.name == "Year 12"
    assert level.slug == "y12"
    assert level.category == "Year"
    assert level.number == "12"


def test_row_to_domain_does_not_mutate_input(mapper):
    row = make_row()
    original = row.copy()

    mapper.row_to_domain(row)

    assert row == original  # ensures domain mapping is pure


# ---------------------------------------------------------------------------
# create_to_params
# ---------------------------------------------------------------------------


def test_create_to_params_returns_all_fields_in_order(mapper):
    data = LevelCreate(
        name="Key Stage 5",
        slug="ks5",
        category="Key Stage",
        number="5",
    )

    params = mapper.create_to_params(data)

    assert params == ("Key Stage 5", "ks5", "Key Stage", "5")


def test_create_to_params_handles_unusual_values(mapper):
    data = LevelCreate(
        name="A Very Custom Level",
        slug="avcl",
        category="Custom Category",
        number="X",
    )

    params = mapper.create_to_params(data)

    assert params == ("A Very Custom Level", "avcl", "Custom Category", "X")
