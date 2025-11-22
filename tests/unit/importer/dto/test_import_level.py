import pytest

from frayerstore.core.utils.slugify import slugify
from frayerstore.importer.dto.import_level import ImportLevel
from frayerstore.importer.exceptions import InvalidYamlStructure


# ---------------------------------------------------------------------------
# VALID CASES
# ---------------------------------------------------------------------------


def test_from_yaml_valid_minimal():
    data = {"name": "Key Stage 4"}
    item = ImportLevel.from_yaml(data, subject_pk=42)

    assert isinstance(item, ImportLevel)
    assert item.subject_pk == 42
    assert item.name == "Key Stage 4"
    # Delegate slug expectations to the real slugify
    assert item.slug == slugify("Key Stage 4")


def test_from_yaml_trims_whitespace_but_preserves_internal_spaces():
    data = {"name": "   A   Level   "}
    item = ImportLevel.from_yaml(data, subject_pk=1)

    # trimmed but internal spaces preserved
    assert item.name == "A   Level"
    assert item.slug == slugify("A   Level")


def test_from_yaml_uses_slugify_with_stripped_name(monkeypatch):
    captured = {}

    def fake_slugify(value: str) -> str:
        captured["value"] = value
        return "sentinel-slug"

    # Patch the slugify that ImportLevel actually uses
    monkeypatch.setattr(
        "frayerstore.importer.dto.import_level.slugify",
        fake_slugify,
    )

    data = {"name": "  Key Stage 4  "}
    item = ImportLevel.from_yaml(data, subject_pk=99)

    # from_yaml should strip before calling slugify
    assert captured["value"] == "Key Stage 4"
    assert item.slug == "sentinel-slug"
    assert item.subject_pk == 99
    assert item.name == "Key Stage 4"


# ---------------------------------------------------------------------------
# ERROR CASES
# ---------------------------------------------------------------------------


def test_from_yaml_non_mapping_raises():
    data = ["not", "a", "mapping"]
    with pytest.raises(InvalidYamlStructure) as exc:
        ImportLevel.from_yaml(data, subject_pk=1)

    assert str(exc.value) == "Level must be a mapping"


@pytest.mark.parametrize(
    "payload",
    [
        {},  # missing
        {"name": ""},  # empty
        {"name": "   "},  # whitespace only
    ],
)
def test_from_yaml_missing_or_blank_name_raises(payload):
    with pytest.raises(InvalidYamlStructure) as exc:
        ImportLevel.from_yaml(payload, subject_pk=1)

    assert str(exc.value) == "Level missing required field 'name'"


def test_from_yaml_non_string_name_raises():
    data = {"name": 123}
    with pytest.raises(InvalidYamlStructure) as exc:
        ImportLevel.from_yaml(data, subject_pk=1)

    assert str(exc.value) == "Level missing required field 'name'"


# ---------------------------------------------------------------------------
# STABILITY / SHAPE TESTS
# ---------------------------------------------------------------------------


def test_from_yaml_slug_is_lowercase_where_applicable():
    data = {"name": "Key Stage 10"}
    item = ImportLevel.from_yaml(data, subject_pk=1)

    # We don't assume exact format, just that letters are lowercased
    assert item.slug == slugify("Key Stage 10")
    assert item.slug == item.slug.lower()
