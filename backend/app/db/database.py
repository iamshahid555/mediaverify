import sqlite3
from datetime import datetime
from pathlib import Path

# Database file location
DB_PATH = Path(__file__).resolve().parent.parent / "mediaverify.db"


def _utc_now() -> str:
    return datetime.utcnow().isoformat()


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _ensure_column(
    cursor: sqlite3.Cursor,
    table_name: str,
    column_name: str,
    definition: str,
):
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_columns = {row[1] for row in cursor.fetchall()}

    if column_name not in existing_columns:
        cursor.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}"
        )


def _row_to_dict(row: sqlite3.Row | None) -> dict | None:
    if row is None:
        return None
    return dict(row)


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def init_db():
    """
    Initialize the SQLite database and create tables if needed.
    """
    conn = _connect()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            password_salt TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            last_used_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            input_type TEXT NOT NULL,
            credibility_score REAL NOT NULL,
            credibility_label TEXT NOT NULL,
            confidence REAL NOT NULL,
            content_preview TEXT,
            source_url TEXT,
            source_domain TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    _ensure_column(cursor, "analyses", "user_id", "INTEGER")
    _ensure_column(cursor, "analyses", "content_preview", "TEXT")
    _ensure_column(cursor, "analyses", "source_url", "TEXT")
    _ensure_column(cursor, "analyses", "source_domain", "TEXT")

    conn.commit()
    conn.close()


def create_user(
    full_name: str,
    email: str,
    password_hash: str,
    password_salt: str,
) -> dict:
    normalized_email = _normalize_email(email)
    conn = _connect()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (
                full_name,
                email,
                password_hash,
                password_salt,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                full_name.strip(),
                normalized_email,
                password_hash,
                password_salt,
                _utc_now(),
            ),
        )
        user_id = cursor.lastrowid
        conn.commit()
    except sqlite3.IntegrityError as exc:
        conn.close()
        raise ValueError("An account with this email already exists.") from exc

    row = conn.execute(
        """
        SELECT id, full_name, email, created_at
        FROM users
        WHERE id = ?
        """,
        (user_id,),
    ).fetchone()
    conn.close()
    return dict(row)


def get_user_by_email(email: str) -> dict | None:
    conn = _connect()
    row = conn.execute(
        """
        SELECT id, full_name, email, password_hash, password_salt, created_at
        FROM users
        WHERE email = ?
        """,
        (_normalize_email(email),),
    ).fetchone()
    conn.close()
    return _row_to_dict(row)


def create_session(user_id: int, token: str):
    conn = _connect()
    conn.execute(
        """
        INSERT INTO sessions (
            token,
            user_id,
            created_at,
            last_used_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (token, user_id, _utc_now(), _utc_now()),
    )
    conn.commit()
    conn.close()


def delete_session(token: str):
    conn = _connect()
    conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
    conn.commit()
    conn.close()


def get_user_by_session_token(token: str) -> dict | None:
    conn = _connect()
    row = conn.execute(
        """
        SELECT u.id, u.full_name, u.email, u.created_at
        FROM sessions s
        JOIN users u ON u.id = s.user_id
        WHERE s.token = ?
        """,
        (token,),
    ).fetchone()

    if row is not None:
        conn.execute(
            "UPDATE sessions SET last_used_at = ? WHERE token = ?",
            (_utc_now(), token),
        )
        conn.commit()

    conn.close()
    return _row_to_dict(row)


def save_analysis(
    user_id: int,
    input_type: str,
    credibility_score: float,
    credibility_label: str,
    confidence: float,
    content_preview: str | None = None,
    source_url: str | None = None,
    source_domain: str | None = None,
):
    """
    Save analysis result into the database.
    """
    conn = _connect()
    conn.execute(
        """
        INSERT INTO analyses (
            user_id,
            input_type,
            credibility_score,
            credibility_label,
            confidence,
            content_preview,
            source_url,
            source_domain,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            input_type,
            credibility_score,
            credibility_label,
            confidence,
            content_preview,
            source_url,
            source_domain,
            _utc_now(),
        ),
    )
    conn.commit()
    conn.close()


def get_analysis_history(user_id: int) -> list[dict]:
    """
    Retrieve saved analysis records for a specific user.
    """
    conn = _connect()
    rows = conn.execute(
        """
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
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,),
    ).fetchall()
    conn.close()

    return [dict(row) for row in rows]
