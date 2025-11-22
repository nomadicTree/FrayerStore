import pytest
from frayerstore.importer.dto.import_subject import ImportSubject
from frayerstore.importer.exceptions import InvalidYamlStructure


def test_from_yaml_valid():
    data = {"name": "Computing"}
    item = ImportSubject.from_yaml(data)

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
