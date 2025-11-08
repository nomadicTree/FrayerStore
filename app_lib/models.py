import json
from app_lib.repositories import get_topics_for_word, get_subject_name


class Word:
    def __init__(self, row):
        self.id = row["id"]
        self.word = row["word"]
        self.definition = (
            row["definition"] if "definition" in row.keys() else ""
        )
        self.characteristics = (
            json.loads(row["characteristics"])
            if "characteristics" in row.keys()
            else []
        )
        self.examples = (
            json.loads(row["examples"]) if "examples" in row.keys() else []
        )
        self.non_examples = (
            json.loads(row["non_examples"])
            if "non_examples" in row.keys()
            else []
        )
        self.subject_name = get_subject_name(row["subject_id"])

        topic_rows = get_topics_for_word(self.id)

        self.topics = [dict(r) for r in topic_rows]

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "word": self.word,
            "definition": self.definition,
            "characteristics": self.characteristics,
            "examples": self.examples,
            "non_examples": self.non_examples,
            "subject_name": self.subject_name,
            "topics": self.topics,
        }
