import sqlite3
from frayerstore.models.topic import Topic
from frayerstore.models.topic_create import TopicCreate


class TopicMapper:
    def row_to_domain(self, row: sqlite3.Row) -> Topic:
        return Topic(
            pk=row["id"],
            course_pk=row["course_id"],
            code=row["code"],
            name=row["name"],
            slug=row["slug"],
        )

    def create_to_params(self, data: TopicCreate) -> tuple:
        return (data.course_pk, data.code, data.name, data.slug)
