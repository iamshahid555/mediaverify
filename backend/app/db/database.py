import sqlite3
from datetime import datetime
from pathlib import Path

# Database file location
DB_PATH = Path(__file__).resolve().parent.parent / "mediaverify.db"


def _ensure_column(cursor: sqlite3.Cursor, column_name: str, definition: str):
    cursor.execute("PRAGMA table_info(analyses)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    if column_name not in existing_columns:
        cursor.execute(f"ALTER TABLE analyses ADD COLUMN {column_name} {definition}")


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
            content_preview TEXT,
            source_url TEXT,
            source_domain TEXT,
            created_at TEXT NOT NULL
        )
    """)

    _ensure_column(cursor, "content_preview", "TEXT")
    _ensure_column(cursor, "source_url", "TEXT")
    _ensure_column(cursor, "source_domain", "TEXT")

    conn.commit()
    conn.close()


def save_analysis(input_type: str,
                  credibility_score: float,
                  credibility_label: str,
                  confidence: float,
                  content_preview: str | None = None,
                  source_url: str | None = None,
                  source_domain: str | None = None):
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
            content_preview,
            source_url,
            source_domain,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        input_type,
        credibility_score,
        credibility_label,
        confidence,
        content_preview,
        source_url,
        source_domain,
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
            content_preview,
            source_url,
            source_domain,
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
            "content_preview": row[5],
            "source_url": row[6],
            "source_domain": row[7],
            "created_at": row[8]
        })

    return history
