from __future__ import annotations
from dataclasses import dataclass

from frayerstore.core.utils.slugify import slugify
from frayerstore.importer.exceptions import InvalidYamlStructure
from frayerstore.importer.dto.import_item import ImportItem


@dataclass(frozen=True)
class ImportLevel(ImportItem):
    subject_pk: int

    @classmethod
    def from_yaml(cls, data: dict, *, subject_pk: int) -> ImportLevel:
        if not isinstance(data, dict):
            raise InvalidYamlStructure("Level must be a mapping")

        name = data.get("name")
        if not name or not isinstance(name, str) or not name.strip():
            raise InvalidYamlStructure("Level missing required field 'name'")

        name = name.strip()
        slug = slugify(name)
        return cls(subject_pk=subject_pk, name=name, slug=slug)
