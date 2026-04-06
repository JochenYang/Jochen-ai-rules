# context-codebase/scripts/context_engine/semantic_chunker.py
"""
Semantic chunker - AST-based intelligent chunking
"""
from __future__ import annotations
import ast
import hashlib
from dataclasses import dataclass
from typing import Iterator

SMALL_FILE_LINES = 60
MEDIUM_FILE_LINES = 150

class SemanticChunker:
    """AST-based semantic chunker"""

    def chunk_file(self, content: str, filepath: str, language: str) -> list[dict]:
        """Chunk a file using semantic boundaries"""
        # Normalize path format, avoid Windows backslash causing ID format errors
        filepath = filepath.replace('\\', '/')
        lines = content.splitlines()
        total_lines = len(lines)

        # Small files stay intact (<60 lines), >=60 lines split by AST boundaries
        if total_lines < SMALL_FILE_LINES:
            return [self._create_chunk(filepath, 1, total_lines, "section", "", content, language)]

        # Use AST for Python
        if language == 'python':
            try:
                tree = ast.parse(content)
                ast_chunks = self._chunk_by_ast_boundaries(tree, content, filepath, language)
                if ast_chunks:
                    return ast_chunks
            except SyntaxError:
                pass
                
        # Use Regex for JS/TS/Go etc
        regex_chunks = self._chunk_by_regex_boundaries(content, filepath, language)
        if regex_chunks:
            return regex_chunks

        return self._chunk_by_lines(content, filepath, language)

    def _chunk_by_ast_boundaries(self, tree: ast.AST, content: str, filepath: str, language: str) -> list[dict]:
        """Split by AST boundaries, only top-level nodes"""
        chunks = []
        lines = content.splitlines()

        # Only process top-level nodes (direct children of Module)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                    start = node.lineno
                    end = node.end_lineno

                    if start and end:
                        chunk_lines = lines[start-1:end]
                        chunk_content = '\n'.join(chunk_lines)

                        kind = "class" if isinstance(node, ast.ClassDef) else "function"
                        name = node.name
                        signals = self._extract_signals(chunk_content, name, language)

                        chunks.append({
                            "id": f"{filepath}:{start}-{end}",
                            "path": filepath,
                            "startLine": start,
                            "endLine": end,
                            "kind": kind,
                            "name": name,
                            "signals": signals,
                            "content": chunk_content,
                            "preview": chunk_content[:200],
                            "language": language
                        })

        # No AST nodes, split by lines
        if not chunks:
            return []

        return chunks

    def _chunk_by_regex_boundaries(self, content: str, filepath: str, language: str) -> list[dict]:
        """Split by regex boundaries for JS/TS/Go"""
        import re
        chunks = []
        lines = content.splitlines()
        
        # Matches JS/TS/Go/Java classes and functions
        pattern = re.compile(
            r'^(?:export\s+)?(?:default\s+)?(?:async\s+)?(?:function|class|func)\s+([a-zA-Z0-9_]+)'
            r'|^(?:export\s+)?(?:const|let|var)\s+([a-zA-Z0-9_]+)\s*[:=].*?(?:=>|function)',
            re.MULTILINE
        )
        
        matches = list(pattern.finditer(content))
        if not matches:
            return []
            
        for i, match in enumerate(matches):
            start_pos = match.start()
            start_line = content.count('\n', 0, start_pos) + 1
            name = match.group(1) or match.group(2) or "unknown"
            kind = "class" if "class" in match.group() else "function"
            
            end_line = len(lines)
            if i + 1 < len(matches):
                end_pos = matches[i+1].start()
                end_line = content.count('\n', 0, end_pos)
                
            chunk_content = '\n'.join(lines[start_line-1:end_line])
            chunks.append(self._create_chunk(filepath, start_line, end_line, kind, name, chunk_content, language))
            
        return chunks

    def _chunk_by_lines(self, content: str, filepath: str, language: str) -> list[dict]:
        """Split by fixed line count (fallback)"""
        chunks = []
        lines = content.splitlines()
        total = len(lines)

        for i in range(0, total, SMALL_FILE_LINES):
            start = i + 1
            end = min(i + SMALL_FILE_LINES, total)
            chunk_lines = lines[i:i+SMALL_FILE_LINES]
            chunk_content = '\n'.join(chunk_lines)

            chunks.append({
                "id": f"{filepath}:{start}-{end}",
                "path": filepath,
                "startLine": start,
                "endLine": end,
                "kind": "section",
                "name": "",
                "signals": self._extract_signals(chunk_content, "", language),
                "content": chunk_content,
                "preview": chunk_content[:200],
                "language": language
            })

        return chunks

    def _extract_signals(self, content: str, name: str, language: str) -> list[str]:
        """Extract semantic signals from content"""
        import re
        signals = set()

        # Extract from name
        if name:
            signals.update(re.findall(r'[a-z]+', name.lower()))

        # Extract from comments/docstrings
        docstrings = re.findall(r'"""(.*?)"""', content, re.DOTALL)
        docstrings += re.findall(r"'''(.*?)'''", content, re.DOTALL)
        for doc in docstrings:
            signals.update(re.findall(r'[a-z]+', doc.lower()))

        # Extract from code keywords
        keywords = [
            'auth', 'login', 'password', 'token', 'jwt', 'session',
            'api', 'http', 'request', 'response', 'endpoint',
            'database', 'db', 'sql', 'query',
            'cache', 'redis', 'memcache',
            'file', 'upload', 'download', 'storage',
            'email', 'notification', 'webhook',
            'payment', 'stripe', 'billing',
            'config', 'settings', 'env',
            'error', 'exception', 'retry',
            'async', 'await', 'promise',
            'middleware', 'hook', 'filter',
            'validation', 'schema', 'type',
        ]
        content_lower = content.lower()
        for kw in keywords:
            if kw in content_lower:
                signals.add(kw)

        return sorted(list(signals))[:20]

    def _create_chunk(self, filepath: str, start: int, end: int, kind: str, name: str, content: str, language: str) -> dict:
        """Create a single chunk"""
        return {
            "id": f"{filepath}:{start}-{end}",
            "path": filepath,
            "startLine": start,
            "endLine": end,
            "kind": kind,
            "name": name,
            "signals": self._extract_signals(content, name, language),
            "content": content,
            "preview": content[:200],
            "language": language
        }