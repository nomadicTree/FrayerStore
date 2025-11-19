import pytest

from frayerstore.core.utils.slugify import slugify


@pytest.mark.parametrize(
    "name, expected",
    [
        ("Computing", "computing"),
        ("Computer Science", "computer-science"),
        ("  Data   Structures ", "data-structures"),
        ("AI & ML", "ai-ml"),
        ("C++ Programming", "c-programming"),
    ],
)
def test_valid_slugify(name, expected):
    assert slugify(name) == expected


def test_slugify_lowercases():
    assert slugify("HeLLo") == "hello"


@pytest.mark.parametrize(
    "name, expected",
    [
        ("A---B", "a-b"),
        ("A__B", "a-b"),
        ("A & B", "a-b"),
        ("A   B", "a-b"),
    ],
)
def test_slugify_collapse_separators(name, expected):
    assert slugify(name) == expected


@pytest.mark.parametrize(
    "name, expected",
    [
        ("Café", "cafe"),
        ("naïve", "naive"),
        ("Gödel", "godel"),
        ("façade", "facade"),
        ("Δelta", "elta"),  # non-latin characters removed
    ],
)
def test_slugify_unicode(name, expected):
    assert slugify(name) == expected


def test_slugify_mixed_noise():
    assert slugify("Hello!!!***???World") == "hello-world"


@pytest.mark.parametrize("bad", ["", " ", "   ", "\n"])
def test_slugify_empty_or_whitespace(bad):
    with pytest.raises(ValueError):
        slugify(bad)


@pytest.mark.parametrize("bad", [1, True, ["hello"]])
def test_slugify_non_str(bad):
    with pytest.raises(TypeError):
        slugify(bad)
