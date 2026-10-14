"""SQLite persistence for analysis history."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager

SCHEMA = """
CREATE TABLE IF NOT EXISTS analyses (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    text        TEXT    NOT NULL,
    label       TEXT    NOT NULL CHECK (label IN ('POSITIVE', 'NEGATIVE', 'NEUTRAL')),
    confidence  REAL    NOT NULL,
    positive    REAL    NOT NULL,
    neutral     REAL    NOT NULL,
    negative    REAL    NOT NULL,
    created_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);
CREATE INDEX IF NOT EXISTS idx_analyses_created ON analyses (created_at DESC);
"""


class Database:
    def __init__(self, path: str):
        self.path = path
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def insert(self, text: str, result) -> dict:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO analyses (text, label, confidence, positive, neutral, negative) VALUES (?, ?, ?, ?, ?, ?)",
                (text, result.label, result.confidence, result.positive, result.neutral, result.negative),
            )
            row = conn.execute("SELECT * FROM analyses WHERE id = ?", (cur.lastrowid,)).fetchone()
        return dict(row)

    def history(self, limit: int = 20, label: str | None = None) -> list[dict]:
        query = "SELECT * FROM analyses"
        params: list = []
        if label:
            query += " WHERE label = ?"
            params.append(label)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            return [dict(r) for r in conn.execute(query, params).fetchall()]

    def delete(self, analysis_id: int) -> bool:
        with self._connect() as conn:
            return conn.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,)).rowcount > 0

    def clear(self) -> int:
        with self._connect() as conn:
            return conn.execute("DELETE FROM analyses").rowcount

    def stats(self) -> dict:
        with self._connect() as conn:
            rows = conn.execute("SELECT label, COUNT(*) AS n, AVG(confidence) AS avg FROM analyses GROUP BY label").fetchall()
        counts = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}
        avg = {}
        for r in rows:
            counts[r["label"]] = r["n"]
            avg[r["label"]] = round(r["avg"], 4)
        return {"total": sum(counts.values()), "counts": counts, "averageConfidence": avg}
