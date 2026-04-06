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
    """SQLite-based chunk index using FTS5 for high-speed full text search"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema with FTS5"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # FTS5 table
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5(
                id UNINDEXED,
                path,
                start_line UNINDEXED,
                end_line UNINDEXED,
                kind,
                name,
                language,
                signals,
                preview,
                content_hash UNINDEXED,
                tokenize="unicode61"
            )
        """)

        conn.commit()
        conn.close()

    def upsert_chunks(self, chunks: list[dict]) -> None:
        """Batch insert or update chunks, clearing old ones first"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for chunk in chunks:
            chunk_id = chunk["id"]
            signals_json = json.dumps(chunk.get("signals", []))
            
            # FTS5 doesn't support UPSERT or INSERT OR REPLACE simply based on an unindexed column constraints
            # We must delete existing matching id first manually
            cursor.execute("DELETE FROM chunks WHERE id = ?", (chunk_id,))
            
            cursor.execute("""
                INSERT INTO chunks
                (id, path, start_line, end_line, kind, name, language, signals, preview)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                chunk_id,
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
        """Search chunks using FTS5 MATCH with BM25 ranking"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Normalize query for FTS5 (escape quotes, split words)
        safe_query = " ".join([f'"{word.replace('"', "")}"' for word in query.split() if word.strip()])
        if not safe_query:
             safe_query = f'"{query.replace('"', "")}"'

        try:
            cursor.execute("""
                SELECT * FROM chunks
                WHERE chunks MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (safe_query, limit))
            
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
        except sqlite3.OperationalError:
            # Fallback if query syntax is invalid
            results = []

        conn.close()
        return results

    def get_by_path(self, path: str) -> list[dict]:
        """Get all chunks for a specific path"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        safe_path = f'"{path.replace('"', "")}"'
        try:
            cursor.execute("SELECT * FROM chunks WHERE path MATCH ?", (safe_path,))
            
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
        except sqlite3.OperationalError:
            results = []

        conn.close()
        return results

    def delete_stale(self, valid_ids: set[str]) -> None:
        """Delete chunks not in valid_ids"""
        if not valid_ids:
            return

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Need to read all IDs since FTS5 doesn't easily support NOT IN for unindexed columns like standard tables
        cursor.execute("SELECT id FROM chunks")
        all_ids = {row["id"] for row in cursor.fetchall()}
        
        # Safety check: skip deletion if none of valid_ids exist in DB
        # Prevents accidental full DB wipe (e.g., when valid_ids is stale)
        if not (valid_ids & all_ids):
            conn.close()
            return

        to_delete = all_ids - valid_ids
        for stale_id in to_delete:
            cursor.execute("DELETE FROM chunks WHERE id = ?", (stale_id,))

        conn.commit()
        conn.close()

    def close(self):
        """Close connection"""
        pass
