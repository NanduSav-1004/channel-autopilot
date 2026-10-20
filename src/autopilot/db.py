"""SQLite job store: one row per video, tracking the last completed stage."""
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    source_title TEXT,
    kind TEXT NOT NULL,            -- long | short
    stage TEXT NOT NULL DEFAULT 'new',
    status TEXT NOT NULL DEFAULT 'pending',  -- pending | done | failed
    attempts INTEGER NOT NULL DEFAULT 0,
    error TEXT,
    video_id TEXT,
    thumbnail_set INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def connect(path: str | Path = "data/autopilot.db") -> sqlite3.Connection:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    cols = {r[1] for r in conn.execute("PRAGMA table_info(jobs)")}
    if "thumbnail_set" not in cols:  # databases created before this column existed
        conn.execute("ALTER TABLE jobs ADD COLUMN thumbnail_set INTEGER NOT NULL DEFAULT 0")
        conn.commit()
    return conn


def add_job(conn: sqlite3.Connection, topic: str, kind: str, source_title: str | None = None) -> int:
    cur = conn.execute(
        "INSERT INTO jobs (topic, kind, source_title) VALUES (?, ?, ?)", (topic, kind, source_title)
    )
    conn.commit()
    return cur.lastrowid


def known_topics(conn: sqlite3.Connection) -> set[str]:
    """Lower-cased topics and source titles already queued or made, for de-duplication."""
    rows = conn.execute("SELECT topic, source_title FROM jobs").fetchall()
    return {v.lower() for r in rows for v in (r["topic"], r["source_title"]) if v}


def pending_count(conn: sqlite3.Connection, kind: str) -> int:
    return conn.execute(
        "SELECT COUNT(*) FROM jobs WHERE kind = ? AND status = 'pending'", (kind,)
    ).fetchone()[0]
