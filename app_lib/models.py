import json
from app_lib.repositories import get_topics_for_word, get_subject_name
from app_lib.utils import render_frayer


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

    def display_frayer(self, show_subject=False, show_topics=False):
        subject = self.subject_name if show_subject else None
        topics = self.topics if show_topics else None
        render_frayer(
            self.id,
            self.word,
            self.definition,
            self.characteristics,
            self.examples,
            self.non_examples,
            subject_name=subject,
            topics=topics,
        )
