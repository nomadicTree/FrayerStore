import pytest

from frayerstore.importer.dto.import_level import ImportLevel
from frayerstore.importer.exceptions import InvalidYamlStructure
from frayerstore.importer.utils import missing_required_field_message


# ---------------------------------------------------------------------------
# VALID CASES
# ---------------------------------------------------------------------------


def test_from_yaml_valid_minimal():
    data = {"category": "Key Stage", "number": "4"}
    item = ImportLevel.from_yaml(data)

    assert item.category == "Key Stage"
    assert item.number == "4"
    assert item.name == "Key Stage 4"
    assert item.slug == "ks4"


def test_from_yaml_trims_whitespace():
    data = {"category": "   Key   Stage  ", "number": "   4   "}
    item = ImportLevel.from_yaml(data)

    assert item.category == "Key   Stage"  # internal spacing preserved
    assert item.number == "4"
    assert item.name == "Key   Stage 4"
    assert item.slug == "ks4"


def test_from_yaml_abbreviation_and_slug_logic():
    data = {"category": "Computer Science", "number": "2"}
    item = ImportLevel.from_yaml(data)

    # abbreviation logic → C + S = "CS"
    assert item.slug == "cs2"
    assert item.name == "Computer Science 2"


# ---------------------------------------------------------------------------
# ERROR CASES
# ---------------------------------------------------------------------------


def test_from_yaml_missing_category_raises():
    data = {"number": "4"}
    with pytest.raises(InvalidYamlStructure) as exc:
        ImportLevel.from_yaml(data)

    assert "Level missing required field 'category'" in str(exc.value)


def test_from_yaml_missing_number_raises():
    data = {"category": "Key Stage"}
    with pytest.raises(InvalidYamlStructure) as exc:
        ImportLevel.from_yaml(data)

    assert "Level missing required field 'number'" in str(exc.value)


def test_from_yaml_category_empty_raises():
    data = {"category": "   ", "number": "4"}
    with pytest.raises(InvalidYamlStructure) as exc:
        ImportLevel.from_yaml(data)

    assert "Level missing required field 'category'" in str(exc.value)


def test_from_yaml_number_empty_raises():
    data = {"category": "Key Stage", "number": "     "}
    with pytest.raises(InvalidYamlStructure) as exc:
        ImportLevel.from_yaml(data)

    assert "Level missing required field 'number'" in str(exc.value)


def test_from_yaml_non_string_values_are_handled():
    data = {"category": 123, "number": 4}
    with pytest.raises(InvalidYamlStructure):
        # .strip() would fail, so our own validation intercepts
        ImportLevel.from_yaml(data)


# ---------------------------------------------------------------------------
# STABILITY TESTS
# ---------------------------------------------------------------------------


def test_from_yaml_slug_is_lowercase():
    data = {"category": "Key Stage", "number": "10"}
    item = ImportLevel.from_yaml(data)
    assert item.slug == item.slug.lower()


def test_from_yaml_slug_comes_from_abbreviation():
    data = {"category": "Advanced Level", "number": "1"}
    item = ImportLevel.from_yaml(data)
    # abbreviation = "AL" → slug = "al1"
    assert item.slug == "al1"
