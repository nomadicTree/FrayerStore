import json

from dataclasses import dataclass

from urllib.parse import quote_plus
from app.core.models.topic_model import Topic
from app.core.models.level_model import Level
from app.core.models.subject_model import Subject
from app.core.models.course_model import Course


class UrlMixin:
    @property
    def url(self):
        return f"/view?id={self.pk}"


@dataclass
class RelatedWord(UrlMixin):
    word_id: str
    word: str


@dataclass(eq=False, order=False)
class WordVersion:
    pk: int
    word: str
    word_id: int
    definition: str
    characteristics: list
    examples: list
    non_examples: list
    topics: list[Topic]
    levels: list[Level]

    def __post_init__(self):
        # Normalise list-like fields
        self.characteristics = self._ensure_list(self.characteristics)
        self.examples = self._ensure_list(self.examples)
        self.non_examples = self._ensure_list(self.non_examples)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WordVersion):
            return NotImplemented
        return self.pk == other.pk

    def __hash__(self) -> int:
        return hash(self.pk)

    def __lt__(self, other):
        if not isinstance(other, WordVersion):
            return NotImplemented
        return self.word.lower() < other.word.lower()

    @property
    def level_label(self) -> str:
        """Return a human-readable label for this WordVersion's levels."""
        levels = [l.name for l in self.levels]

        if not levels:
            return "All levels"
        if len(levels) == 1:
            return levels[0]
        if len(levels) == 2:
            return " and ".join(levels)
        return ", ".join(levels[:-1]) + f", and {levels[-1]}"

    @property
    def url(self) -> str:
        level_param = quote_plus(self.level_label)
        return f"/view?id={self.pk}&level={level_param}"

    @property
    def courses(self) -> set[Course]:
        return {t.course for t in self.topics}

    def _ensure_list(self, value):
        # Case 1: Already a real list (preview mode)
        if isinstance(value, list):
            return value

        # Case 2: None or empty string → treat as empty list
        if not value:
            return []

        # Case 3: A JSON string → decode it
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
            return []
        except Exception:
            return []


class WordVersionChoice:
    def __init__(self, version: WordVersion):
        self.version = version

    @property
    def name(self) -> str:
        return self.version.level_label


@dataclass(eq=False, order=False)
class Word(UrlMixin):
    pk: int
    word: str
    subject: Subject
    versions: list[WordVersion]
    related_words: list[RelatedWord]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Word):
            return NotImplemented
        return self.pk == other.pk

    def __hash__(self) -> int:
        return hash(self.pk)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Word):
            return NotImplemented
        return self.word.lower() < other.word.lower()

    @property
    def courses(self) -> set[Course]:
        return {c for v in self.versions for c in v.courses}
