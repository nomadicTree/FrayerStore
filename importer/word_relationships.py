import sqlite3
import pandas as pd
import streamlit as st
import os

# -------------------------------------------------------------------
# Database path
# -------------------------------------------------------------------

DB_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "db",
    "Words.db",
)

conn = sqlite3.connect(DB_FILE)

# -------------------------------------------------------------------
# Load Words + aggregated WordVersions text
# -------------------------------------------------------------------

df = pd.read_sql_query(
    """
    SELECT 
        w.id AS word_id,
        w.word AS word,
        LOWER(GROUP_CONCAT(COALESCE(wv.definition, ''), ' ')) AS definition,
        LOWER(GROUP_CONCAT(COALESCE(wv.characteristics, ''), ' ')) AS characteristics,
        LOWER(GROUP_CONCAT(COALESCE(wv.examples, ''), ' ')) AS examples,
        LOWER(GROUP_CONCAT(COALESCE(wv.non_examples, ''), ' ')) AS non_examples
    FROM Words w
    LEFT JOIN WordVersions wv ON w.id = wv.word_id
    GROUP BY w.id
    """,
    conn,
)

# Single searchable block
df["all_text"] = (
    df["definition"].fillna("")
    + " "
    + df["characteristics"].fillna("")
    + " "
    + df["examples"].fillna("")
    + " "
    + df["non_examples"].fillna("")
).astype(str)


# -------------------------------------------------------------------
# Load existing word-word relationships (IDs only)
# -------------------------------------------------------------------

existing_rel = pd.read_sql_query(
    "SELECT word_id1, word_id2 FROM WordRelationships",
    conn,
)

existing_pairs = {
    tuple(sorted((row["word_id1"], row["word_id2"])))
    for _, row in existing_rel.iterrows()
}


# -------------------------------------------------------------------
# Find NEW relationships
# -------------------------------------------------------------------


def find_candidate_relationships(df):
    relationships = set()

    for i, row_i in df.iterrows():
        word_i = row_i["word"].lower()
        id_i = row_i["word_id"]

        for j, row_j in df.iterrows():
            if i == j:
                continue

            id_j = row_j["word_id"]
            combined = row_j["all_text"]

            if not combined:
                continue

            # If word_i appears in row_j text
            if word_i in combined:
                pair_ids = tuple(sorted((id_i, id_j)))
                relationships.add(pair_ids)

    # Remove existing relationships
    new_rel = [(a, b) for (a, b) in relationships if (a, b) not in existing_pairs]

    # Build DataFrame for UI
    rows = []
    for a, b in new_rel:
        word1 = df.loc[df["word_id"] == a, "word"].iloc[0]
        word2 = df.loc[df["word_id"] == b, "word"].iloc[0]
        rows.append((a, word1, b, word2))

    return pd.DataFrame(rows, columns=["id1", "word1", "id2", "word2"])


# -------------------------------------------------------------------
# Run detector
# -------------------------------------------------------------------

candidates_df = find_candidate_relationships(df)


# -------------------------------------------------------------------
# Streamlit UI
# -------------------------------------------------------------------

st.title("Approve Word Relationships")

approved_rows = []

if candidates_df.empty:
    st.info("No new candidate relationships found.")
else:
    for _, row in candidates_df.iterrows():
        st.markdown(f"**{row['word1']} ↔ {row['word2']}**")

        approve = st.radio(
            "Approve this relationship?",
            ("No", "Yes"),
            key=f"{row['id1']}_{row['id2']}",
        )

        if approve == "Yes":
            approved_rows.append((row["id1"], row["id2"]))


# -------------------------------------------------------------------
# Save new relationships
# -------------------------------------------------------------------

if st.button("Save approved relationships"):
    with conn:
        for id1, id2 in approved_rows:
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

    st.success(f"{len(approved_rows)} new relationships saved.")
