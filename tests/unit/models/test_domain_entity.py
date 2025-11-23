from dataclasses import dataclass, field

from frayerstore.models.domain_entity import DomainEntity


@dataclass(eq=False)
class Foo(DomainEntity):
    slug: str = "foo"
    name: str = "x"


@dataclass(eq=False)
class Bar(DomainEntity):
    slug: str = "bar"
    name: str = "bar"
    value: int = 0


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

    # should hit "type(other) is not type(self)" branch → NotImplemented → False
    assert (a == b) is False
    assert (b == a) is False
    assert hash(a) != hash(b)


def test_comparison_with_non_domain_entity_returns_not_implemented():
    a = Foo(pk=1)

    # a == 123 → NotImplemented → Python resolves that to False
    assert (a == 123) is False


def test_hash_is_stable_and_based_on_type_and_pk():
    a1 = Foo(pk=42)
    a2 = Foo(pk=42)
    b = Bar(pk=42)

    # same type + same pk → same hash
    assert hash(a1) == hash(a2)

    # different type + same pk → different hash
    assert hash(a1) != hash(b)

    # stable across calls
    assert hash(a1) == hash(a1)


def test_entities_work_in_sets_and_dicts():
    a = Foo(pk=1)
    b = Foo(pk=1)
    c = Foo(pk=2)

    s = {a, c}
    assert b in s
    assert len(s) == 2

    d = {a: "hello"}
    assert d[b] == "hello"
