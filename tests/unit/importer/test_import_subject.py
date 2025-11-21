import pytest
from frayerstore.importer.exceptions import InvalidYamlStructure
from frayerstore.importer.subjects import ImportSubject


def test_from_yaml_valid():
    data = {"subject": "Computing"}
    item = ImportSubject.from_yaml(data)

    assert item.id is None
    assert item.name == "Computing"
    assert item.slug == "computing"


def test_from_yaml_missing_key_raises():
    data = {}
    with pytest.raises(InvalidYamlStructure):
        ImportSubject.from_yaml(data)


def test_from_yaml_empty_subject_raises():
    data = {"subject": "   "}  # whitespace only
    with pytest.raises(InvalidYamlStructure):
        ImportSubject.from_yaml(data)
