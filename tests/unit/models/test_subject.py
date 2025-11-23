from frayerstore.models.subject import Subject


def test_subject_creation():
    name = "Computing"
    slug = "computing"
    a = Subject(pk=1, name=name, slug=slug)
    assert a.pk == 1
    assert a.name == name
    assert a.slug == slug
    assert a.label == name
