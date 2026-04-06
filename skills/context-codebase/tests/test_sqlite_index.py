# context-codebase/tests/test_sqlite_index.py
import pytest
import sys
import tempfile
import os
from pathlib import Path

# 设置正确的导入路径
SCRIPT_DIR = Path(__file__).resolve().parents[1] / 'scripts'
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from context_engine.sqlite_index import SQLiteIndex


class TestSQLiteIndex:
    def setup_method(self):
        """每个测试前创建临时数据库"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.index = SQLiteIndex(self.db_path)

    def teardown_method(self):
        """清理临时文件"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_upsert_and_search(self):
        """插入后能搜索到"""
        chunks = [
            {
                "id": "test.py:1-10",
                "path": "test.py",
                "startLine": 1,
                "endLine": 10,
                "kind": "function",
                "name": "authenticate",
                "signals": ["auth", "login"],
                "preview": "def authenticate...",
                "language": "python"
            }
        ]

        self.index.upsert_chunks(chunks)
        results = self.index.search("auth")

        assert len(results) == 1
        assert results[0]["id"] == "test.py:1-10"

    def test_get_by_path(self):
        """按路径获取 chunks"""
        chunks = [
            {
                "id": "test.py:1-10",
                "path": "test.py",
                "startLine": 1,
                "endLine": 10,
                "kind": "function",
                "name": "foo",
                "signals": [],
                "preview": "...",
                "language": "python"
            },
            {
                "id": "test.py:12-20",
                "path": "test.py",
                "startLine": 12,
                "endLine": 20,
                "kind": "function",
                "name": "bar",
                "signals": [],
                "preview": "...",
                "language": "python"
            }
        ]

        self.index.upsert_chunks(chunks)
        results = self.index.get_by_path("test.py")

        assert len(results) == 2

    def test_delete_stale(self):
        """删除废弃 chunks"""
        chunks = [
            {
                "id": "test.py:1-10",
                "path": "test.py",
                "startLine": 1,
                "endLine": 10,
                "kind": "function",
                "name": "foo",
                "signals": [],
                "preview": "...",
                "language": "python"
            }
        ]

        self.index.upsert_chunks(chunks)
        # 只保留这个 ID
        self.index.delete_stale({"test.py:1-10"})

        # 验证还在
        results = self.index.search("foo")
        assert len(results) == 1

        # 删除不存在的
        self.index.delete_stale({"nonexistent"})

        # 验证仍然在
        results = self.index.search("foo")
        assert len(results) == 1

    def test_replace_existing(self):
        """替换已存在的 chunk"""
        chunk = {
            "id": "test.py:1-10",
            "path": "test.py",
            "startLine": 1,
            "endLine": 10,
            "kind": "function",
            "name": "foo",
            "signals": ["original"],
            "preview": "original",
            "language": "python"
        }

        self.index.upsert_chunks([chunk])

        # 用相同 ID 但不同内容替换
        chunk["signals"] = ["updated"]
        chunk["preview"] = "updated"
        self.index.upsert_chunks([chunk])

        results = self.index.search("updated")
        assert len(results) == 1
        assert results[0]["signals"] == ["updated"]
