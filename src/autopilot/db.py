"""SQLite job store: one row per video, tracking the last completed stage."""
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    kind TEXT NOT NULL,            -- long | short
    stage TEXT NOT NULL DEFAULT 'new',
    status TEXT NOT NULL DEFAULT 'pending',  -- pending | done | failed
    attempts INTEGER NOT NULL DEFAULT 0,
    error TEXT,
    video_id TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def connect(path: str | Path = "data/autopilot.db") -> sqlite3.Connection:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def add_job(conn: sqlite3.Connection, topic: str, kind: str) -> int:
    cur = conn.execute("INSERT INTO jobs (topic, kind) VALUES (?, ?)", (topic, kind))
    conn.commit()
    return cur.lastrowid
