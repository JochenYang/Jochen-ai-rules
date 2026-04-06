import pytest
import sys
from pathlib import Path

# 设置正确的导入路径
SCRIPT_DIR = Path(__file__).resolve().parents[1] / 'scripts'
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from context_engine.chunk_tracker import ChunkTracker, ChunkState, ChangeSet

class TestChunkTracker:
    def test_track_generates_stable_ids(self):
        """相同 chunk 应生成相同的 ID"""
        tracker = ChunkTracker()

        chunks = [
            {"id": "test.py:1-10", "content": "def foo():\n    pass"},
            {"id": "test.py:12-20", "content": "def bar():\n    pass"},
        ]

        states = tracker.track(chunks)

        assert "test.py:1-10" in states
        assert "test.py:12-20" in states
        assert states["test.py:1-10"].version == 1

    def test_detect_modified_chunk(self):
        """能检测到 chunk 的修改"""
        tracker = ChunkTracker()

        old_chunks = [
            {"id": "test.py:1-10", "content": "def foo():\n    return 1"},
        ]
        old_states = tracker.track(old_chunks)

        new_chunks = [
            {"id": "test.py:1-10", "content": "def foo():\n    return 42"},
        ]
        new_states = tracker.track(new_chunks)

        diff = tracker.diff(old_states, new_states)

        assert len(diff.modified) == 1
        assert diff.modified[0]["id"] == "test.py:1-10"

    def test_detect_added_chunk(self):
        """能检测到新增的 chunk"""
        tracker = ChunkTracker()

        old_chunks = [
            {"id": "test.py:1-10", "content": "def foo():\n    pass"},
        ]
        old_states = tracker.track(old_chunks)

        new_chunks = [
            {"id": "test.py:1-10", "content": "def foo():\n    pass"},
            {"id": "test.py:12-20", "content": "def bar():\n    pass"},
        ]
        new_states = tracker.track(new_chunks)

        diff = tracker.diff(old_states, new_states)

        assert len(diff.added) == 1
        assert diff.added[0]["id"] == "test.py:12-20"

    def test_detect_deleted_chunk(self):
        """能检测到删除的 chunk"""
        tracker = ChunkTracker()

        old_chunks = [
            {"id": "test.py:1-10", "content": "def foo():\n    pass"},
            {"id": "test.py:12-20", "content": "def bar():\n    pass"},
        ]
        old_states = tracker.track(old_chunks)

        new_chunks = [
            {"id": "test.py:1-10", "content": "def foo():\n    pass"},
        ]
        new_states = tracker.track(new_chunks)

        diff = tracker.diff(old_states, new_states)

        assert len(diff.deleted) == 1
        assert "test.py:12-20" in diff.deleted

    def test_unchanged_chunk_version_increment(self):
        """未变更的 chunk 版本不变"""
        tracker = ChunkTracker()

        chunks = [
            {"id": "test.py:1-10", "content": "def foo():\n    pass"},
        ]
        v1 = tracker.track(chunks)

        v2 = tracker.track(chunks)

        assert v1["test.py:1-10"].content_hash == v2["test.py:1-10"].content_hash

    def test_merge_states_increments_version(self):
        """合并状态时版本号递增"""
        tracker = ChunkTracker()

        old_chunks = [
            {"id": "test.py:1-10", "content": "def foo():\n    pass"},
        ]
        old_states = tracker.track(old_chunks)

        new_chunks = [
            {"id": "test.py:1-10", "content": "def foo():\n    return 42"},
        ]
        new_states = tracker.track(new_chunks)

        merged = tracker.merge_states(old_states, new_states)

        assert merged["test.py:1-10"].version == 2