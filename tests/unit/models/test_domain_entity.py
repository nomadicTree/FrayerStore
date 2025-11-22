from dataclasses import dataclass
from frayerstore.models.domain_entity import DomainEntity


# Concrete subclasses
@dataclass(frozen=True)
class Foo(DomainEntity):
    name: str = "x"


@dataclass(frozen=True)
class Bar(DomainEntity):
    value: int = 0


# ---------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------


def test_equal_when_same_type_and_same_pk():
    a = Foo(pk=1)
    b = Foo(pk=1)

    assert a == b
    assert hash(a) == hash(b)


def test_not_equal_when_same_type_but_different_pk():
    a = Foo(pk=1)
    b = Foo(pk=2)

    assert a != b
    assert hash(a) != hash(b)


def test_not_equal_across_subclasses_even_if_same_pk():
    a = Foo(pk=1)
    b = Bar(pk=1)

    assert a != b
    assert (a == b) is False
    # hash differs because we include type in hash
    assert hash(a) != hash(b)


def test_comparison_with_non_domain_entity_returns_not_implemented():
    a = Foo(pk=1)

    # This becomes "False" because Python interprets NotImplemented
    assert (a == 123) is False


def test_hash_is_stable_and_based_on_type_and_pk():
    a = Foo(pk=42)

    # Hash is deterministic
    assert hash(a) == hash(Foo(pk=42))

    # And different subclass should produce different hash
    assert hash(Foo(pk=42)) != hash(Bar(pk=42))

    # Hash is stable on repeated calls
    assert hash(a) == hash(a)


def test_entities_work_in_sets_and_dicts():
    a = Foo(pk=1)
    b = Foo(pk=1)
    c = Foo(pk=2)

    s = {a, c}
    assert b in s  # same type + same pk
    assert len(s) == 2

    d = {a: "hello"}
    assert d[b] == "hello"
