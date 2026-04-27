import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / 'scripts'
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from context_engine.analyzers import JavaScriptAnalyzer
from context_engine.multi_lang_analyzer import MultiLangAnalyzer

class TestMultiLangAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = MultiLangAnalyzer()

    def test_supports_python(self):
        self.assertTrue(self.analyzer.supports(".py"))

    def test_supports_typescript(self):
        self.assertTrue(self.analyzer.supports(".ts"))

    def test_supports_go(self):
        self.assertTrue(self.analyzer.supports(".go"))

    def test_supports_rust(self):
        self.assertTrue(self.analyzer.supports(".rs"))

    def test_analyze_python(self):
        content = """
import fastapi

def hello():
    return {"message": "hello"}
"""
        result = self.analyzer.analyze(content, "test.py")

        self.assertEqual(result["language"], "python")
        self.assertIn("fastapi", result["imports"])
        self.assertIn("hello", result["key_functions"])

    def test_analyze_go(self):
        content = """
package main

import "fmt"

func main() {
    fmt.Println("Hello")
}
"""
        result = self.analyzer.analyze(content, "test.go")

        self.assertEqual(result["language"], "go")
        self.assertIn("fmt", result["imports"])
        self.assertIn("main", result["key_functions"])

    def test_analyze_rust(self):
        content = """
fn main() {
    println!("Hello, world!");
}
"""
        result = self.analyzer.analyze(content, "test.rs")

        self.assertEqual(result["language"], "rust")
        self.assertIn("main", result["key_functions"])

    def test_analyze_javascript(self):
        content = """
import { foo } from 'bar';

export function hello() {
    return 'world';
}
"""
        result = self.analyzer.analyze(content, "test.js")

        self.assertEqual(result["language"], "javascript")
        self.assertIn("bar", result["imports"])
        self.assertIn("hello", result["exports"])

    def test_analyze_typescript(self):
        content = """
import { User } from './models';

export class Service {
    greet() {
        return 'hi';
    }
}
"""
        result = self.analyzer.analyze(content, "test.ts")

        self.assertEqual(result["language"], "typescript")
        self.assertIn("./models", result["imports"])
        self.assertIn("Service", result["exports"])

    def test_typescript_ast_bridge_uses_utf8_stdio(self):
        analyzer = JavaScriptAnalyzer(Path("bridge.js"))
        captured: dict[str, object] = {}

        class FakeCompleted:
            returncode = 0
            stdout = '{"ok": false}'

        def fake_run(*args, **kwargs):
            captured["args"] = args
            captured["kwargs"] = kwargs
            return FakeCompleted()

        import context_engine.analyzers as analyzers_module

        original_run = analyzers_module.subprocess.run
        try:
            analyzers_module.subprocess.run = fake_run
            analyzer._analyze_with_typescript_ast(
                'export const label = "emoji 😀";',
                "src/demo.ts",
                "D:/codes/demo",
            )
        finally:
            analyzers_module.subprocess.run = original_run

        kwargs = captured["kwargs"]
        self.assertTrue(kwargs["text"])
        self.assertEqual(kwargs["encoding"], "utf-8")
        self.assertEqual(kwargs["errors"], "strict")
        self.assertEqual(kwargs["input"], 'export const label = "emoji 😀";')


if __name__ == "__main__":
    unittest.main()
