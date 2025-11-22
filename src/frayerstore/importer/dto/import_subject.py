from __future__ import annotations
from dataclasses import dataclass
from frayerstore.core.utils.slugify import slugify
from frayerstore.importer.utils import missing_required_field_message
from frayerstore.importer.exceptions import InvalidYamlStructure
from frayerstore.importer.dto.import_item import ImportItem


@dataclass(frozen=True)
class ImportSubject(ImportItem):
    @classmethod
    def from_yaml(cls, data: dict) -> ImportSubject:
        required_fields = ["name"]

        for field in required_fields:
            message = missing_required_field_message("Level", field)
            value = data.get(field)
            if value is None:
                raise InvalidYamlStructure(message)

            if not isinstance(value, str):
                raise InvalidYamlStructure(message)

            if not value.strip():
                raise InvalidYamlStructure(message)

        name = data["name"].strip()
        slug = slugify(name)
        return cls(name=name, slug=slug)
