from app.core.db import get_db
from app.core.models.subject_model import Subject


def get_subjects():
    """Get all Subjects

    Returns:
        List of all Subjects
    """
    db = get_db()

    q = """
        SELECT * FROM Subjects
    """
    rows = db.execute(q).fetchall()

    subjects = [
        Subject(
            subject_id=r["id"],
            name=r["name"],
        )
        for r in rows
    ]

    return subjects
