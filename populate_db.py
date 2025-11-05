import os
import sqlite3
import json
import yaml
import shutil
from datetime import datetime

DB_FILE = "data/words.db"
SCHEMA_FILE = "data/schema.sql"
YAML_FILE = "data/words.yaml"
BACKUP_DIR = "data/backups"


# -------------------------------
# Helper Functions (from before)
# -------------------------------
def get_or_create_subject(cursor, name):
    cursor.execute("SELECT id FROM Subject WHERE name=?", (name,))
    res = cursor.fetchone()
    if res:
        return res[0]
    cursor.execute("INSERT INTO Subject(name) VALUES(?)", (name,))
    return cursor.lastrowid


def get_or_create_course(cursor, name, subject_id):
    cursor.execute(
        "SELECT id FROM Course WHERE name=? AND subject_id=?",
        (name, subject_id),
    )
    res = cursor.fetchone()
    if res:
        return res[0]
    cursor.execute(
        "INSERT INTO Course(name, subject_id) VALUES(?, ?)",
        (name, subject_id),
    )
    return cursor.lastrowid


def get_or_create_topic(cursor, code, name, course_id):
    cursor.execute(
        "SELECT id FROM Topic WHERE code=? AND course_id=?",
        (code, course_id),
    )
    res = cursor.fetchone()
    if res:
        return res[0]
    cursor.execute(
        "INSERT INTO Topic(code, name, course_id) VALUES(?, ?, ?)",
        (code, name, course_id),
    )
    return cursor.lastrowid


def get_or_create_word(cursor, word_data, subject_id):
    cursor.execute(
        "SELECT id FROM Word WHERE word=? AND subject_id=?",
        (word_data["word"], subject_id),
    )
    res = cursor.fetchone()

    characteristics = json.dumps(word_data.get("characteristics", []))
    examples = json.dumps(word_data.get("examples", []))
    non_examples = json.dumps(word_data.get("non-examples", []))

    if res:
        word_id = res[0]
        # Update definition/fields if needed
        cursor.execute(
            """
            UPDATE Word SET
                definition=?,
                characteristics=?,
                examples=?,
                non_examples=?
            WHERE id=?
            """,
            (
                word_data.get("definition"),
                characteristics,
                examples,
                non_examples,
                word_id,
            ),
        )
        return word_id
    else:
        cursor.execute(
            """
            INSERT INTO Word(word, subject_id, definition, characteristics, examples, non_examples)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                word_data["word"],
                subject_id,
                word_data.get("definition"),
                characteristics,
                examples,
                non_examples,
            ),
        )
        return cursor.lastrowid


def link_word_to_topic(cursor, word_id, topic_id):
    cursor.execute(
        "SELECT 1 FROM WordTopic WHERE word_id=? AND topic_id=?",
        (word_id, topic_id),
    )
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO WordTopic(word_id, topic_id) VALUES(?, ?)",
            (word_id, topic_id),
        )


def create_db_if_not_exists(db_path, schema_path):
    if not os.path.exists(db_path):
        print(f"Database not found, creating new DB at {db_path}")
        conn = sqlite3.connect(db_path)
        with open(schema_path) as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()


def backup_db(db_path):
    os.makedirs(BACKUP_DIR, exist_ok=True)

    # Current timestamp in YYYYMMDD_HHMMSS format
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Extract the base name of the DB file (e.g., 'words.db')
    base_name = os.path.basename(db_path)

    # Construct backup filename: words.db_YYYYMMDD_HHMMSS.bak
    backup_filename = f"{base_name}_{timestamp}.bak"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)

    shutil.copy2(db_path, backup_path)
    print(f"Backup created: {backup_path}")


# -------------------------------
# Main import function
# -------------------------------
def import_words_yaml(
    yaml_file=YAML_FILE, db_file=DB_FILE, schema_file=SCHEMA_FILE
):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(script_dir, yaml_file)
    db_path = os.path.join(script_dir, db_file)
    schema_path = os.path.join(script_dir, schema_file)

    # 1️⃣ Create DB if it doesn't exist
    create_db_if_not_exists(db_path, schema_path)

    # 2️⃣ Backup DB before modifying
    backup_db(db_path)

    # 3️⃣ Load YAML
    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Lookup dictionary for topics
    topic_lookup = {}

    # Insert Subjects → Courses → Topics
    for subj in data["subjects"]:
        subject_id = get_or_create_subject(cursor, subj["name"])
        for course in subj["courses"]:
            course_id = get_or_create_course(
                cursor, course["name"], subject_id
            )
            for topic in course["topics"]:
                topic_id = get_or_create_topic(
                    cursor, topic["code"], topic["name"], course_id
                )
                topic_lookup[(course["name"], topic["code"])] = (
                    topic_id,
                    course_id,
                    subject_id,
                )

    # Insert Words and link to topics
    for word in data["words"]:
        for topic_ref in word.get("topics", []):
            course_name = topic_ref["course"]
            for code in topic_ref["codes"]:
                lookup = topic_lookup.get((course_name, code))
                if lookup:
                    topic_id, course_id, subject_id = lookup
                    word_id = get_or_create_word(cursor, word, subject_id)
                    link_word_to_topic(cursor, word_id, topic_id)

    conn.commit()
    conn.close()
    print("Import complete. Database backed up and updated.")


# -------------------------------
# Run import if main
# -------------------------------
if __name__ == "__main__":
    import_words_yaml()
