import pytest

from frayerstore.importer.identity import (
    handle_resolution,
    resolve_identity,
    IdentityResolutionResult,
    ImportDecision,
)

from frayerstore.models.subject import Subject
from frayerstore.importer.exceptions import SubjectImportError
from frayerstore.importer.dto.import_subject import ImportSubject


# HELPERS
def make_subject(
    pk: int,
    name: str,
    slug: str,
) -> Subject:
    return Subject(pk=pk, name=name, slug=slug)


def make_import_subject(name: str, slug: str) -> ImportSubject:
    return ImportSubject(name=name, slug=slug)


# TESTS
def test_handle_resolution_error_raises_and_records(stage_report):
    res = IdentityResolutionResult(
        decision=ImportDecision.ERROR,
        error="Something bad happened",
    )

    with pytest.raises(SubjectImportError):
        handle_resolution(res, SubjectImportError, stage_report)

    assert stage_report.errors == ["Something bad happened"]


def test_handle_resolution_skip_records(stage_report):
    existing = make_subject(1, "Computing", "computing")

    res = IdentityResolutionResult(
        decision=ImportDecision.SKIP,
        existing=existing,
    )

    out = handle_resolution(res, SubjectImportError, stage_report)

    assert out == existing
    assert stage_report.skipped == [existing]


def test_handle_resolution_create_returns_none(stage_report):
    res = IdentityResolutionResult(decision=ImportDecision.CREATE)

    out = handle_resolution(res, SubjectImportError, stage_report)

    assert out is None
    assert stage_report.skipped == []
    assert stage_report.errors == []


def test_resolve_identity_double_collision_returns_error():
    incoming = make_import_subject("Computing", "computing")
    slug_row = make_subject(1, "Computing", "computing")
    name_row = make_subject(2, "Different", "different")

    out = resolve_identity(incoming, slug_row, name_row)
    assert out.decision == ImportDecision.ERROR
    assert "Identity conflict" in out.error


def test_resolve_identity_slug_match_name_mismatch_is_error():
    incoming = make_import_subject("Maths", "maths")
    existing = make_subject(1, "Mathematics", "maths")

    out = resolve_identity(incoming, existing, None)
    assert out.decision == ImportDecision.ERROR
    assert "Identity conflict" in out.error


def test_resolve_identity_slug_match_identical_is_skip():
    incoming = make_import_subject("Computing", "computing")
    existing = make_subject(1, "Computing", "computing")

    out = resolve_identity(incoming, existing, None)
    assert out.decision == ImportDecision.SKIP
    assert out.existing == existing


def test_resolve_identity_name_match_slug_mismatch_is_error():
    incoming = make_import_subject("Computing", "comp")
    existing = make_subject(1, "Computing", "computing")

    out = resolve_identity(incoming, None, existing)
    assert out.decision == ImportDecision.ERROR
    assert "Identity conflict" in out.error


def test_resolve_identity_name_match_identical_is_skip():
    incoming = make_import_subject("Computing", "computing")
    existing = make_subject(1, "Computing", "computing")

    out = resolve_identity(incoming, None, existing)
    assert out.decision == ImportDecision.SKIP


def test_resolve_identity_neither_match_is_create():
    incoming = make_import_subject("Computing", "computing")

    out = resolve_identity(incoming, None, None)
    assert out.decision == ImportDecision.CREATE
