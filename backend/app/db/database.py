import sqlite3
from pathlib import Path
from datetime import datetime

# Database file location
DB_PATH = Path(__file__).resolve().parent.parent / "mediaverify.db"


def init_db():
    """
    Initialize the SQLite database and create table if not exists.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input_type TEXT NOT NULL,
            credibility_score REAL NOT NULL,
            credibility_label TEXT NOT NULL,
            confidence REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_analysis(input_type: str,
                  credibility_score: float,
                  credibility_label: str,
                  confidence: float):
    """
    Save analysis result into database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO analyses (
            input_type,
            credibility_score,
            credibility_label,
            confidence,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        input_type,
        credibility_score,
        credibility_label,
        confidence,
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()


def get_analysis_history():
    """
    Retrieve all saved analysis records.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            input_type,
            credibility_score,
            credibility_label,
            confidence,
            created_at
        FROM analyses
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    history = []

    for row in rows:
        history.append({
            "id": row[0],
            "input_type": row[1],
            "credibility_score": row[2],
            "credibility_label": row[3],
            "confidence": row[4],
            "created_at": row[5]
        })

    return history