import pytest
from context_engine.multi_lang_analyzer import MultiLangAnalyzer

class TestMultiLangAnalyzer:
    def setup_method(self):
        self.analyzer = MultiLangAnalyzer()

    def test_supports_python(self):
        assert self.analyzer.supports(".py")

    def test_supports_typescript(self):
        assert self.analyzer.supports(".ts")

    def test_supports_go(self):
        assert self.analyzer.supports(".go")

    def test_supports_rust(self):
        assert self.analyzer.supports(".rs")

    def test_analyze_python(self):
        content = """
import fastapi

def hello():
    return {"message": "hello"}
"""
        result = self.analyzer.analyze(content, "test.py")

        assert result["language"] == "python"
        assert "fastapi" in result["imports"]
        assert "hello" in result["key_functions"]

    def test_analyze_go(self):
        content = """
package main

import "fmt"

func main() {
    fmt.Println("Hello")
}
"""
        result = self.analyzer.analyze(content, "test.go")

        assert result["language"] == "go"
        assert "fmt" in result["imports"]
        assert "main" in result["key_functions"]

    def test_analyze_rust(self):
        content = """
fn main() {
    println!("Hello, world!");
}
"""
        result = self.analyzer.analyze(content, "test.rs")

        assert result["language"] == "rust"
        assert "main" in result["key_functions"]

    def test_analyze_javascript(self):
        content = """
import { foo } from 'bar';

export function hello() {
    return 'world';
}
"""
        result = self.analyzer.analyze(content, "test.js")

        assert result["language"] == "javascript"
        assert "bar" in result["imports"]
        assert "hello" in result["exports"]

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

        assert result["language"] == "typescript"
        assert "./models" in result["imports"]
        assert "Service" in result["exports"]