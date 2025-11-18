import sqlite3
import pandas as pd
import streamlit as st
import os

# ================================================================
# Configuration
# ================================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_FILE = os.path.join(BASE_DIR, "db", "Words.db")
IGNORE_FILE = os.path.join(BASE_DIR, "ignored_relationships.txt")

conn = sqlite3.connect(DB_FILE)


# ================================================================
# Helpers
# ================================================================


def load_ignore_list():
    """
    Load ignored relationships from file.
    Only returns ID pairs, but the file contains word + subject info too.
    """
    ignored = set()

    if os.path.exists(IGNORE_FILE):
        with open(IGNORE_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                # Expected format:
                # id1,word1,subject1,id2,word2,subject2
                if len(parts) == 6:
                    id1, _, _, id2, _, _ = parts
                    a, b = sorted((int(id1), int(id2)))
                    ignored.add((a, b))

    return ignored


def save_ignored_pairs(pairs, df_words):
    """
    Write ignored pairs to file including:
    id1,word1,subject_slug1,id2,word2,subject_slug2
    """
    if not pairs:
        return

    with open(IGNORE_FILE, "a", encoding="utf-8") as f:
        for id1, id2 in pairs:
            a, b = sorted((id1, id2))

            row_a = df_words.loc[df_words["word_id"] == a].iloc[0]
            row_b = df_words.loc[df_words["word_id"] == b].iloc[0]

            subj1 = row_a["subject_slug"]
            subj2 = row_b["subject_slug"]

            f.write(f"{a},{row_a['word']},{subj1},{b},{row_b['word']},{subj2}\n")


# ================================================================
# Load DB Data
# ================================================================


@st.cache_data(show_spinner=False)
def load_word_data():
    """
    Load words, WordVersions text, synonyms, and subject slug.
    """
    df_words = pd.read_sql_query(
        """
        SELECT 
            w.id AS word_id,
            w.word AS word,
            s.slug AS subject_slug,
            LOWER(GROUP_CONCAT(COALESCE(wv.definition, ''), ' ')) AS definition,
            LOWER(GROUP_CONCAT(COALESCE(wv.characteristics, ''), ' ')) AS characteristics,
            LOWER(GROUP_CONCAT(COALESCE(wv.examples, ''), ' ')) AS examples,
            LOWER(GROUP_CONCAT(COALESCE(wv.non_examples, ''), ' ')) AS non_examples
        FROM Words w
        JOIN Subjects s ON s.id = w.subject_id
        LEFT JOIN WordVersions wv ON w.id = wv.word_id
        GROUP BY w.id
        """,
        conn,
    )

    # Combine all text into a single field
    df_words["all_text"] = (
        df_words["definition"].fillna("")
        + " "
        + df_words["characteristics"].fillna("")
        + " "
        + df_words["examples"].fillna("")
        + " "
        + df_words["non_examples"].fillna("")
    ).astype(str)

    # Load synonyms
    df_syns = pd.read_sql_query(
        "SELECT word_id, LOWER(synonym) AS synonym FROM Synonyms",
        conn,
    )

    synmap = df_syns.groupby("word_id")["synonym"].apply(list).to_dict()

    df_words["synonyms"] = (
        df_words["word_id"]
        .map(synmap)
        .fillna("")
        .apply(lambda x: x if isinstance(x, list) else [])
    )

    # Add synonyms to searchable block
    df_words["all_text"] += " " + df_words["synonyms"].apply(lambda s: " ".join(s))

    return df_words


def load_existing_relationships():
    rel = pd.read_sql_query(
        "SELECT word_id1, word_id2 FROM WordRelationships",
        conn,
    )

    return {
        tuple(sorted((row["word_id1"], row["word_id2"]))) for _, row in rel.iterrows()
    }


# ================================================================
# Relationship Detection
# ================================================================


def find_candidate_relationships(df_words, existing_pairs, ignored_pairs):
    """Find relationships based on text and synonyms."""
    relationships = set()

    for i, row_i in df_words.iterrows():
        id_i = row_i["word_id"]
        word_i = row_i["word"].lower()
        synonyms_i = row_i["synonyms"]

        for j, row_j in df_words.iterrows():
            if i == j:
                continue

            id_j = row_j["word_id"]
            combined = row_j["all_text"]

            if not combined:
                continue

            direct_match = word_i in combined
            synonym_match = any(s in combined for s in synonyms_i)

            if direct_match or synonym_match:
                pair = tuple(sorted((id_i, id_j)))
                relationships.add(pair)

    # Exclude already-existing + ignored
    new_pairs = [
        (a, b)
        for (a, b) in relationships
        if (a, b) not in existing_pairs and (a, b) not in ignored_pairs
    ]

    rows = []
    for a, b in new_pairs:
        w1 = df_words.loc[df_words["word_id"] == a, "word"].iloc[0]
        w2 = df_words.loc[df_words["word_id"] == b, "word"].iloc[0]
        rows.append((a, w1, b, w2))

    return pd.DataFrame(rows, columns=["id1", "word1", "id2", "word2"])


# ================================================================
# Streamlit UI
# ================================================================


def main():
    st.title("Approve Word Relationships")

    df_words = load_word_data()
    existing_pairs = load_existing_relationships()
    ignored_pairs = load_ignore_list()

    candidates_df = find_candidate_relationships(
        df_words, existing_pairs, ignored_pairs
    )

    if candidates_df.empty:
        st.info("No new candidate relationships found.")
        return

    approved = []
    ignored = []

    st.write("Review each proposed relationship:")

    for _, row in candidates_df.iterrows():
        st.markdown(f"### **{row['word1']} ↔ {row['word2']}**")

        choice = st.radio(
            "What do you want to do?",
            ("Skip", "Approve", "Ignore"),
            key=f"{row['id1']}_{row['id2']}",
        )

        if choice == "Approve":
            approved.append((row["id1"], row["id2"]))
        elif choice == "Ignore":
            ignored.append((row["id1"], row["id2"]))

        st.divider()

    # -------------------------------------------------------------------
    # Apply changes
    # -------------------------------------------------------------------

    if st.button("Apply changes"):
        # Save approved relationships
        with conn:
            for id1, id2 in approved:
                a, b = sorted((id1, id2))
                try:
                    conn.execute(
                        """
                        INSERT INTO WordRelationships (word_id1, word_id2)
                        VALUES (?, ?)
                        """,
                        (a, b),
                    )
                except sqlite3.IntegrityError:
                    pass

        # Save ignored pairs (with word + subject metadata)
        save_ignored_pairs(ignored, df_words)

        st.success(
            f"Saved {len(approved)} approved and {len(ignored)} ignored relationships."
        )


# ================================================================
# Run App
# ================================================================

if __name__ == "__main__":
    main()
