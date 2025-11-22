from __future__ import annotations
from dataclasses import dataclass
from frayerstore.core.utils.slugify import slugify
from frayerstore.importer.exceptions import InvalidYamlStructure
from frayerstore.importer.dto.import_item import ImportItem


@dataclass(frozen=True)
class ImportSubject(ImportItem):
    @classmethod
    def from_yaml(cls, data: dict) -> ImportSubject:
        if not isinstance(data, dict):
            raise InvalidYamlStructure("Subject must be a mapping")

        name = data.get("name")
        if not name or not isinstance(name, str) or not name.strip():
            raise InvalidYamlStructure("Subject missing required field 'name'")

        slug = slugify(name)
        name = name.strip()
        return cls(name=name, slug=slug)
