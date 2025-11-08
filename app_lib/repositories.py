"""Database queries"""

from typing import List
import sqlite3
from app_lib.db import get_db


def search_words(query: str) -> List[sqlite3.Row]:
    """Search database for words matching query

    Args:
        query: search query

    Returns:
        Rows of matching words
    """
    query = query.strip()
    db = get_db()
    q = "SELECT * FROM Word WHERE word LIKE ? ORDER BY Word.word"
    rows = db.execute(q, (f"%{query}%",)).fetchall()
    return rows


def get_subject_name(subject_id: int) -> str:
    """Return subject name given its ID

    Args:
        subject_id: subject ID

    Returns:
        Subject name or None if not found
    """
    db = get_db()
    q = "SELECT name FROM Subject WHERE id = ?"
    row = db.execute(q, (subject_id,)).fetchone()
    subject_name = row["name"] if row else None
    return subject_name


def get_topics_for_word(word_id: int) -> List[sqlite3.Row]:
    """Return all topics associated with a given word

    Args:
        word_id: word ID

    Returns:
        Rows corresponding to topics for the word
        Each row contains 'code', 'topic_name', 'course_name', and topic_label fields.
    """
    db = get_db()
    q = """
    SELECT
        Topic.code,
        Topic.name AS topic_name,
        Course.name AS course_name,
        Subject.name AS subject_name,
        Topic.code || ': ' || Topic.name AS topic_label
    FROM Topic
    JOIN WordTopic ON Topic.id = WordTopic.topic_id
    JOIN Course ON Topic.course_id = Course.id
    JOIN Subject ON Course.subject_id = Subject.id
    WHERE WordTopic.word_id = ?
    ORDER BY Course.name, Topic.code
    """
    rows = db.execute(q, (word_id,)).fetchall()
    return rows


def get_all_subjects_courses_topics() -> List[sqlite3.Row]:
    """Return a list of rows containing all subjects, courses, and topics
    Returns:
        Rows corresponding to subjects, courses, and topics
        Each row contains 'subject', 'course', 'topic_id', 'code', 'topic_name', and 'topic_label' fields.
        Ordered by subject name, course name, and topic code.
    """
    db = get_db()
    q = """
    SELECT
    Subject.name as subject,
    Course.name as course,
    Topic.id as topic_id,
    Topic.code,
    Topic.name as topic_name,
    Topic.code || ': ' || Topic.name AS topic_label
    FROM Subject
    JOIN Course ON Subject.id = Course.subject_id
    JOIN Topic ON Course.id = Topic.course_id
    ORDER BY Subject.name, Course.name, Topic.code
    """
    rows = db.execute(q).fetchall()
    return rows


def get_words_by_topic(topic_id: int) -> List[sqlite3.Row]:
    """Return a list of rows containing all words associated with a given topic
    Args:
        topic_id: topic ID
    Returns:
        Rows corresponding to words for the topic
    """
    db = get_db()
    q = """
        SELECT Word.*
        FROM Word
        JOIN WordTopic ON Word.id = WordTopic.word_id
        WHERE WordTopic.topic_id = ?
    """
    rows = db.execute(q, (topic_id,)).fetchall()
    return rows


def get_word_by_id(word_id: int) -> sqlite3.Row:
    """Return row for word given its id

    Args:
        word_id: word ID

    Returns:
        Row corresponding to the word or None if not found
    """
    try:
        word_id = int(word_id)
    except TypeError:
        return None
    db = get_db()
    q = "SELECT * FROM Word WHERE id = ?"
    row = db.execute(q, (word_id,)).fetchone()
    return row
