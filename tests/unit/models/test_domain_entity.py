from frayerstore.models.domain_entity import DomainEntity


def test_entites_with_same_pk_are_equal():
    a = DomainEntity(1)
    b = DomainEntity(1)
    assert a == b


def test_entites_with_different_pk_are_not_equal():
    a = DomainEntity(1)
    b = DomainEntity(2)
    assert a != b
