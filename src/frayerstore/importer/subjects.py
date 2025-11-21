from __future__ import annotations
import sqlite3
from pathlib import Path
from dataclasses import dataclass

from frayerstore.core.utils.slugify import slugify
from .yaml_utils import load_yaml
from .exceptions import SubjectImportCollision, InvalidYamlStructure
from .db import get_subject_by_name, get_subject_by_slug
from .models import ImportItem
from .report import ImportReport
from .identity import import_with_identity


@dataclass(frozen=True)
class ImportSubject(ImportItem):
    @classmethod
    def from_yaml(cls, data: dict) -> ImportSubject:
        if "subject" not in data or not data["subject"].strip():
            raise InvalidYamlStructure(
                "Subject definition missing required field 'subject'."
            )
        name = data["subject"].strip()
        slug = slugify(name)
        return cls(id=None, name=name, slug=slug)

    @classmethod
    def create_in_db(cls, conn: sqlite3.Row, incoming: ImportSubject) -> ImportSubject:
        from .db import insert_subject

        new_id = insert_subject(conn, incoming)
        return incoming.with_id(new_id)


def import_subject(
    conn: sqlite3.Connection, yaml_path: Path, report: ImportReport
) -> ImportSubject:
    """Import a unique subject to the database"""
    data = load_yaml(yaml_path)
    incoming = ImportSubject.from_yaml(data)

    # Fetch DB matches
    slug_row = get_subject_by_slug(conn, incoming.slug)
    name_row = get_subject_by_name(conn, incoming.name)

    existing_by_slug = ImportSubject.from_row(slug_row) if slug_row else None
    existing_by_name = ImportSubject.from_row(name_row) if name_row else None

    return import_with_identity(
        conn,
        incoming,
        existing_by_slug=existing_by_slug,
        existing_by_name=existing_by_name,
        stage_report=report.subjects,
        exception_type=SubjectImportCollision,
    )
