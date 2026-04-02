"""
Multi-language analyzer - supports all major languages
"""
from __future__ import annotations
import ast
import re
from pathlib import Path
from typing import Optional

class MultiLangAnalyzer:
    """Multi-language analyzer"""

    EXT_TO_LANGUAGE = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".go": "go",
        ".rs": "rust",
        ".java": "java",
        ".cs": "csharp",
        ".php": "php",
        ".rb": "ruby",
        ".c": "cpp",
        ".cpp": "cpp",
        ".cc": "cpp",
        ".cxx": "cpp",
        ".h": "cpp",
        ".hpp": "cpp",
    }

    def supports(self, ext: str) -> bool:
        """Check if this extension is supported"""
        return ext.lower() in self.EXT_TO_LANGUAGE

    def analyze(self, content: str, filepath: str) -> dict:
        """Analyze file content"""
        ext = Path(filepath).suffix.lower()
        language = self.EXT_TO_LANGUAGE.get(ext, "unknown")

        if language == "python":
            return self._analyze_python(content, filepath)
        elif language == "go":
            return self._analyze_go(content, filepath)
        elif language == "rust":
            return self._analyze_rust(content, filepath)
        elif language in ("javascript", "typescript"):
            return self._analyze_js(content, filepath)
        else:
            return self._fallback_analysis(content, filepath, language)

    def _analyze_python(self, content: str, filepath: str) -> dict:
        """Analyze Python file"""
        result = self._base_analysis(content, filepath)
        result["language"] = "python"

        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        result["imports"].append(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        result["imports"].append(node.module.split('.')[0])
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not node.name.startswith('_'):
                        result["key_functions"].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    if not node.name.startswith('_'):
                        result["exports"].append(node.name)
        except SyntaxError:
            pass

        return result

    def _analyze_go(self, content: str, filepath: str) -> dict:
        """Analyze Go file"""
        result = self._base_analysis(content, filepath)
        result["language"] = "go"

        # import "fmt"
        for match in re.finditer(r'import\s+"([^"]+)"', content):
            result["imports"].append(match.group(1))

        # import (
        #     "fmt"
        # )
        for match in re.finditer(r'import\s*\(([^)]+)\)', content, re.DOTALL):
            for imp in re.finditer(r'"([^"]+)"', match.group(1)):
                result["imports"].append(imp.group(1))

        # func main()
        for match in re.finditer(r'func\s+(\w+)\s*\(', content):
            result["key_functions"].append(match.group(1))

        # func (t *T) Method()
        for match in re.finditer(r'func\s+\([^)]+\)\s+(\w+)\s*\(', content):
            if match.group(1) not in result["key_functions"]:
                result["key_functions"].append(match.group(1))

        return result

    def _analyze_rust(self, content: str, filepath: str) -> dict:
        """Analyze Rust file"""
        result = self._base_analysis(content, filepath)
        result["language"] = "rust"

        # use crate::module;
        for match in re.finditer(r'use\s+([^;]+);', content):
            result["imports"].append(match.group(1).split("::")[0])

        # fn function_name()
        for match in re.finditer(r'fn\s+(\w+)\s*[\(<]', content):
            name = match.group(1)
            if not name.startswith('_'):
                result["key_functions"].append(name)

        # struct, enum, trait
        for match in re.finditer(r'(struct|enum|trait)\s+(\w+)', content):
            result["exports"].append(match.group(2))

        return result

    def _analyze_js(self, content: str, filepath: str) -> dict:
        """Analyze JavaScript/TypeScript file"""
        result = self._base_analysis(content, filepath)
        ext = Path(filepath).suffix.lower()
        result["language"] = "typescript" if ext in (".ts", ".tsx") else "javascript"

        # import xxx from 'yyy'
        for match in re.finditer(r"import\s+(?:{\s*)?(\w+)(?:\s*,)?\s*.*?\s+from\s+['\"]([^'\"]+)['\"]", content):
            imp_path = match.group(2)
            # Keep full path for relative imports
            if imp_path.startswith('.'):
                result["imports"].append(imp_path)
            else:
                result["imports"].append(imp_path.split('/')[0])
            if match.group(1):
                result["exports"].append(match.group(1))

        # require('xxx')
        for match in re.finditer(r"require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)", content):
            result["imports"].append(match.group(1).split('/')[0])

        # export function / export const
        for match in re.finditer(r'export\s+(?:function|const|let|var|class)\s+(\w+)', content):
            result["exports"].append(match.group(1))

        # function name()
        for match in re.finditer(r'(?:^|\n)function\s+(\w+)\s*\(', content, re.MULTILINE):
            if match.group(1) not in result["exports"]:
                result["key_functions"].append(match.group(1))

        return result

    def _fallback_analysis(self, content: str, filepath: str, language: str) -> dict:
        """Generic fallback analyzer"""
        result = self._base_analysis(content, filepath)
        result["language"] = language
        return result

    def _base_analysis(self, content: str, filepath: str) -> dict:
        """Base analysis structure"""
        return {
            "path": filepath,
            "imports": [],
            "exports": [],
            "api_routes": [],
            "data_models": [],
            "key_functions": [],
            "framework_hints": [],
            "language": "unknown"
        }