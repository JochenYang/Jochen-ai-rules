"""
Chunk-level incremental tracker
"""
from __future__ import annotations
import hashlib
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ChunkState:
    chunk_id: str
    content_hash: str
    version: int = 1

@dataclass
class ChangeSet:
    added: list[dict] = field(default_factory=list)
    modified: list[dict] = field(default_factory=list)
    deleted: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)

class ChunkTracker:
    """Chunk-level incremental tracker"""

    def track(self, chunks: list[dict]) -> dict[str, ChunkState]:
        """
        Generate stable state records for each chunk
        """
        states = {}

        for chunk in chunks:
            chunk_id = chunk["id"]
            content = chunk.get("content", "")
            content_hash = self._hash_content(content)

            states[chunk_id] = ChunkState(
                chunk_id=chunk_id,
                content_hash=content_hash,
                version=1
            )

        return states

    def diff(self, old: dict[str, ChunkState], new: dict[str, ChunkState]) -> ChangeSet:
        """
        Compare two state sets and return a change set
        """
        change_set = ChangeSet()

        old_ids = set(old.keys())
        new_ids = set(new.keys())

        # Added
        for chunk_id in new_ids - old_ids:
            change_set.added.append({"id": chunk_id})

        # Deleted
        for chunk_id in old_ids - new_ids:
            change_set.deleted.append(chunk_id)

        # Modified and unchanged
        for chunk_id in old_ids & new_ids:
            if old[chunk_id].content_hash != new[chunk_id].content_hash:
                change_set.modified.append({"id": chunk_id})
            else:
                change_set.unchanged.append(chunk_id)

        return change_set

    def merge_states(self, old: dict[str, ChunkState], new: dict[str, ChunkState]) -> dict[str, ChunkState]:
        """
        Merge old and new states, incrementing version numbers
        """
        merged = dict(old)

        for chunk_id, state in new.items():
            if chunk_id in old:
                # Increment version
                merged[chunk_id] = ChunkState(
                    chunk_id=chunk_id,
                    content_hash=state.content_hash,
                    version=old[chunk_id].version + 1
                )
            else:
                merged[chunk_id] = state

        return merged

    def _hash_content(self, content: str) -> str:
        """Compute content hash"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]