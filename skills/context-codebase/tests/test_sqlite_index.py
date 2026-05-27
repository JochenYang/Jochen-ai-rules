# context-codebase/tests/test_sqlite_index.py
import sys
import tempfile
import os
import unittest
from pathlib import Path

# 设置正确的导入路径
SCRIPT_DIR = Path(__file__).resolve().parents[1] / 'scripts'
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from context_engine.sqlite_index import SQLiteIndex


class TestSQLiteIndex(unittest.TestCase):
    def setUp(self):
        """每个测试前创建临时数据库"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.index = SQLiteIndex(self.db_path)

    def tearDown(self):
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

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "test.py:1-10")

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

        self.assertEqual(len(results), 2)

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
        self.assertEqual(len(results), 1)

        # 删除不存在的
        self.index.delete_stale({"nonexistent"})

        # 无交集时应清理为0（避免陈旧数据残留）
        results = self.index.search("foo")
        self.assertEqual(len(results), 0)

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
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["signals"], ["updated"])

    def test_search_handles_quoted_query(self):
        """查询里包含引号时也能正常检索"""
        chunk = {
            "id": "src/router.py:1-10",
            "path": "src/router.py",
            "startLine": 1,
            "endLine": 10,
            "kind": "function",
            "name": "route_message",
            "signals": ["route", "message"],
            "preview": "def route_message(payload): return payload",
            "language": "python",
        }
        self.index.upsert_chunks([chunk])

        results = self.index.search('"message" route')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "src/router.py:1-10")

    def test_get_by_path_handles_wrapped_quotes(self):
        """路径参数带包裹引号时仍可命中"""
        chunk = {
            "id": "src/app.py:1-5",
            "path": "src/app.py",
            "startLine": 1,
            "endLine": 5,
            "kind": "function",
            "name": "main",
            "signals": ["entry"],
            "preview": "def main(): pass",
            "language": "python",
        }
        self.index.upsert_chunks([chunk])

        results = self.index.get_by_path('"src/app.py"')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["path"], "src/app.py")

    # ---- content column + match transparency ---------------------------------

    def test_upsert_includes_content_column(self):
        """插入时 content 字段进入 FTS5，搜索返回的 result 包含 content"""
        chunks = [
            {
                "id": "app.py:1-8",
                "path": "app.py",
                "startLine": 1,
                "endLine": 8,
                "kind": "function",
                "name": "main",
                "signals": [],
                "preview": "def main():",
                "content": "def main():\n    x = 1\n    return x\n",
                "language": "python",
            }
        ]
        self.index.upsert_chunks(chunks)
        results = self.index.search("main")
        self.assertEqual(len(results), 1)
        content = results[0].get("content", "")
        self.assertIn("return x", content)

    def test_get_by_path_includes_content(self):
        """get_by_path 也返回 content 字段"""
        chunks = [
            {
                "id": "lib.py:1-5",
                "path": "lib.py",
                "startLine": 1,
                "endLine": 5,
                "kind": "function",
                "name": "helper",
                "signals": [],
                "preview": "def helper():\n    pass",
                "content": "def helper():\n    pass\n",
                "language": "python",
            }
        ]
        self.index.upsert_chunks(chunks)
        results = self.index.get_by_path("lib.py")
        self.assertEqual(len(results), 1)
        self.assertIn("def helper", results[0].get("content", ""))

    def test_search_returns_matches(self):
        """搜索返回的 result 包含 matches 列表，给出匹配词的行列位置"""
        code = "def authenticate():\n    return token\n"
        chunks = [
            {
                "id": "auth.py:1-5",
                "path": "auth.py",
                "startLine": 1,
                "endLine": 5,
                "kind": "function",
                "name": "authenticate",
                "signals": [],
                "preview": "def authenticate():\n    return token",
                "content": code,
                "language": "python",
            }
        ]
        self.index.upsert_chunks(chunks)
        results = self.index.search("authenticate")
        self.assertEqual(len(results), 1)
        matches = results[0].get("matches", [])
        self.assertGreaterEqual(len(matches), 1)
        # At least one match should point to the right neighbourhood
        file_line = matches[0].get("line", 0)
        self.assertIsInstance(file_line, int)
        self.assertGreaterEqual(file_line, 1)
        self.assertIn("term", matches[0])

    # ---- _compute_matches unit tests -----------------------------------------

    def test_compute_matches_single_line(self):
        """单行内容能正确匹配词条"""
        matches = SQLiteIndex._compute_matches(
            "connect_to_config()", "connect", file_start_line=10,
        )
        self.assertGreaterEqual(len(matches), 1)
        self.assertEqual(matches[0]["term"], "connect")
        self.assertEqual(matches[0]["line"], 10)
        self.assertEqual(matches[0]["col"], 1)

    def test_compute_matches_multi_line(self):
        """跨行内容能正确匹配每行"""
        text = "line1\nline2\nline3"
        matches = SQLiteIndex._compute_matches(text, "line", file_start_line=1)
        self.assertGreaterEqual(len(matches), 3)  # one per line
        lines_found = {m["line"] for m in matches}
        self.assertIn(1, lines_found)
        self.assertIn(2, lines_found)
        self.assertIn(3, lines_found)

    def test_compute_matches_multiple_per_line(self):
        """一行内有多个匹配都能返回"""
        text = "foo bar foo"
        matches = SQLiteIndex._compute_matches(text, "foo", file_start_line=5)
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0]["col"], 1)
        self.assertEqual(matches[1]["col"], 9)

    def test_compute_matches_case_insensitive(self):
        """大小写不敏感"""
        text = "Hello World"
        matches = SQLiteIndex._compute_matches(text, "hello", file_start_line=1)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["term"], "hello")

    def test_compute_matches_empty_input(self):
        """空输入不崩溃"""
        self.assertEqual(SQLiteIndex._compute_matches("", "query", 1), [])
        self.assertEqual(SQLiteIndex._compute_matches("text", "", 1), [])
        self.assertEqual(SQLiteIndex._compute_matches("text", "  ", 1), [])

    def test_compute_matches_no_find(self):
        """无匹配返回空列表"""
        self.assertEqual(SQLiteIndex._compute_matches("aaa", "bbb", 1), [])

    def test_search_matches_via_compute_matches(self):
        """集成测试：search 返回的 matches 与 _compute_matches 一致"""
        code = "def handler():\n    pass\n"
        chunks = [
            {
                "id": "h.py:1-5",
                "path": "h.py",
                "startLine": 1,
                "endLine": 5,
                "kind": "function",
                "name": "handler",
                "signals": [],
                "preview": code[:60],
                "content": code,
                "language": "python",
            }
        ]
        self.index.upsert_chunks(chunks)
        results = self.index.search("handler")
        self.assertEqual(len(results), 1)
        matches = results[0].get("matches", [])
        self.assertGreaterEqual(len(matches), 1)
        # "handler" appears in content line 1 or preview
        self.assertTrue(any("handler" == m["term"] for m in matches))

    def test_get_by_path_is_exact_match(self):
        """路径查询应是精确匹配，避免误命中相似路径"""
        chunks = [
            {
                "id": "src/app.py:1-5",
                "path": "src/app.py",
                "startLine": 1,
                "endLine": 5,
                "kind": "function",
                "name": "main",
                "signals": ["entry"],
                "preview": "def main(): pass",
                "language": "python",
            },
            {
                "id": "src/app.py.bak:1-5",
                "path": "src/app.py.bak",
                "startLine": 1,
                "endLine": 5,
                "kind": "function",
                "name": "main_backup",
                "signals": ["backup"],
                "preview": "def main_backup(): pass",
                "language": "python",
            },
        ]
        self.index.upsert_chunks(chunks)

        results = self.index.get_by_path("src/app.py")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["path"], "src/app.py")


class TestSQLiteIndexIncremental(unittest.TestCase):
    """Test incremental FTS5 upsert behavior"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.index = SQLiteIndex(self.db_path)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _make_chunk(self, path: str, ch_id: str, name: str = "func", signals: list = None,
                    preview: str = "...", kind: str = "function") -> dict:
        return {
            "id": ch_id,
            "path": path,
            "startLine": 1,
            "endLine": 10,
            "kind": kind,
            "name": name,
            "signals": signals or [],
            "preview": preview,
            "language": "python",
        }

    def test_incremental_on_empty_initial(self):
        """首次构建（无已有数据）走增量路径不会报错且正确插入"""
        chunks = [
            self._make_chunk("src/a.py", "src/a.py:1-10", signals=["alpha"], preview="alpha content"),
            self._make_chunk("src/b.py", "src/b.py:1-10", signals=["beta"], preview="beta content"),
        ]
        changed = {"src/a.py", "src/b.py"}

        self.index.upsert_chunks_incremental(chunks, changed)

        results_a = self.index.search("alpha")
        self.assertEqual(len(results_a), 1)
        results_b = self.index.search("beta")
        self.assertEqual(len(results_b), 1)

    def test_incremental_empty_changed_paths(self):
        """changed_paths 为空时不应该有任何操作"""
        initial = [self._make_chunk("src/a.py", "src/a.py:1-10", signals=["alpha"])]
        self.index.upsert_chunks_incremental(initial, set())
        results = self.index.search("alpha")
        self.assertEqual(len(results), 0)

    def test_incremental_only_updates_changed_paths(self):
        """增量更新只替换 changed_paths 中的路径，其余保持不变"""
        initial_chunks = [
            self._make_chunk("src/a.py", "src/a.py:1-10", signals=["alpha"], preview="old alpha"),
            self._make_chunk("src/b.py", "src/b.py:1-10", signals=["beta"], preview="beta"),
            self._make_chunk("src/c.py", "src/c.py:1-10", signals=["gamma"], preview="gamma"),
        ]
        self.index.upsert_chunks(initial_chunks)

        # 增量更新：只改 a.py（内容变化），b.py 和 c.py 不变
        changed_chunks = [
            self._make_chunk("src/a.py", "src/a.py:1-10", signals=["alpha"], preview="new alpha"),
            # b.py 和 c.py 不在 changed_paths 中，所以不会出现在这个列表里
        ]
        self.index.upsert_chunks_incremental(changed_chunks, {"src/a.py"})

        # a.py 的 chunks 应该被更新（新 preview 可搜索到）
        results_a = self.index.search("new alpha")
        self.assertEqual(len(results_a), 1, "新 a.py chunk 应被搜索到")
        # 使用精确的 get_by_path 确认旧 content 已被替换
        a_chunks = self.index.get_by_path("src/a.py")
        self.assertEqual(len(a_chunks), 1, "a.py 仍有 1 个 chunk")
        self.assertEqual(a_chunks[0]["preview"], "new alpha", "a.py chunk 已更新为新内容")

        # b.py 和 c.py 的 chunks 应该保持不变
        results_b = self.index.search("beta")
        self.assertEqual(len(results_b), 1)
        results_c = self.index.search("gamma")
        self.assertEqual(len(results_c), 1)

    def test_incremental_removes_deleted_paths(self):
        """增量更新时，changed_paths 中但不在 chunks 中的路径（已删除文件）的旧 chunk 被清理"""
        initial_chunks = [
            self._make_chunk("src/a.py", "src/a.py:1-10", signals=["alpha"]),
            self._make_chunk("src/b.py", "src/b.py:1-10", signals=["beta"]),
        ]
        self.index.upsert_chunks(initial_chunks)

        # 模拟文件删除：a.py 被删除
        remaining = [
            self._make_chunk("src/b.py", "src/b.py:1-10", signals=["beta"]),
        ]
        self.index.upsert_chunks_incremental(remaining, {"src/a.py"})

        # a.py 的 chunk 应该被删除了
        results_a = self.index.search("alpha")
        self.assertEqual(len(results_a), 0)

        # b.py 的 chunk 还在
        results_b = self.index.search("beta")
        self.assertEqual(len(results_b), 1)

    def test_incremental_matches_full_rebuild(self):
        """增量更新的搜索效果应和全量重建一致"""
        all_chunks = [
            self._make_chunk("src/a.py", "src/a.py:1-10", signals=["alpha", "token"], preview="alpha fn"),
            self._make_chunk("src/b.py", "src/b.py:1-10", signals=["beta", "token"], preview="beta fn"),
            self._make_chunk("src/c.py", "src/c.py:1-10", signals=["gamma"], preview="gamma fn"),
        ]
        # 全量构建
        self.index.upsert_chunks(all_chunks)
        results_full = self.index.search("token", limit=10)
        ids_full = {r["id"] for r in results_full}

        # 重新创建 index 走增量路径
        self.index.close()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.index = SQLiteIndex(self.db_path)

        # 分两步增量构建
        step1 = [self._make_chunk("src/a.py", "src/a.py:1-10", signals=["alpha", "token"], preview="alpha fn")]
        self.index.upsert_chunks_incremental(step1, {"src/a.py"})

        step2 = [
            self._make_chunk("src/b.py", "src/b.py:1-10", signals=["beta", "token"], preview="beta fn"),
            self._make_chunk("src/c.py", "src/c.py:1-10", signals=["gamma"], preview="gamma fn"),
        ]
        self.index.upsert_chunks_incremental(step2, {"src/b.py", "src/c.py"})

        results_incr = self.index.search("token", limit=10)
        ids_incr = {r["id"] for r in results_incr}

        self.assertEqual(ids_full, ids_incr)


if __name__ == "__main__":
    unittest.main()
