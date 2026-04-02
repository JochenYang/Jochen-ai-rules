# context-codebase/scripts/context_engine/sqlite_index.py
"""
SQLite index - high-speed KV query storage
"""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Optional


class SQLiteIndex:
    """SQLite-based chunk index"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                path TEXT NOT NULL,
                start_line INTEGER,
                end_line INTEGER,
                kind TEXT,
                name TEXT,
                language TEXT,
                content_hash TEXT,
                signals TEXT,
                preview TEXT
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_path ON chunks(path)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_kind ON chunks(kind)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_language ON chunks(language)")

        conn.commit()
        conn.close()

    def upsert_chunks(self, chunks: list[dict]) -> None:
        """Batch insert or update chunks"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for chunk in chunks:
            signals_json = json.dumps(chunk.get("signals", []))

            cursor.execute("""
                INSERT OR REPLACE INTO chunks
                (id, path, start_line, end_line, kind, name, language, signals, preview)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                chunk["id"],
                chunk["path"],
                chunk.get("startLine"),
                chunk.get("endLine"),
                chunk.get("kind"),
                chunk.get("name"),
                chunk.get("language"),
                signals_json,
                chunk.get("preview", "")[:200]
            ))

        conn.commit()
        conn.close()

    def search(self, query: str, limit: int = 10) -> list[dict]:
        """Search chunks"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Simple keyword matching
        like_pattern = f"%{query}%"

        cursor.execute("""
            SELECT * FROM chunks
            WHERE path LIKE ? OR signals LIKE ? OR preview LIKE ? OR name LIKE ?
            LIMIT ?
        """, (like_pattern, like_pattern, like_pattern, like_pattern, limit))

        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row["id"],
                "path": row["path"],
                "startLine": row["start_line"],
                "endLine": row["end_line"],
                "kind": row["kind"],
                "name": row["name"],
                "language": row["language"],
                "signals": json.loads(row["signals"]) if row["signals"] else [],
                "preview": row["preview"]
            })

        conn.close()
        return results

    def get_by_path(self, path: str) -> list[dict]:
        """Get all chunks for a specific path"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM chunks WHERE path = ?", (path,))

        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row["id"],
                "path": row["path"],
                "startLine": row["start_line"],
                "endLine": row["end_line"],
                "kind": row["kind"],
                "name": row["name"],
                "language": row["language"],
                "signals": json.loads(row["signals"]) if row["signals"] else [],
                "preview": row["preview"]
            })

        conn.close()
        return results

    def delete_stale(self, valid_ids: set[str]) -> None:
        """Delete chunks not in valid_ids"""
        if not valid_ids:
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Safety check: skip deletion if none of valid_ids exist in DB
        # Prevents accidental full DB wipe (e.g., when valid_ids is stale)
        placeholders = ','.join('?' * len(valid_ids))
        cursor.execute(f"SELECT COUNT(*) FROM chunks WHERE id IN ({placeholders})", tuple(valid_ids))
        count = cursor.fetchone()[0]

        if count == 0:
            # None of valid_ids exist in DB, skip deletion
            conn.close()
            return

        cursor.execute(f"DELETE FROM chunks WHERE id NOT IN ({placeholders})", tuple(valid_ids))

        conn.commit()
        conn.close()

    def close(self):
        """Close connection"""
        pass
