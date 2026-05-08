# context-codebase/scripts/context_engine/fuzzy_search.py
"""
Fuzzy symbol searcher - IDE-like Ctrl+P symbol search.
Step 1: Build symbol index from chunk names
Step 2: Score queries against symbols using fuzzy matching
Step 3: Support camelCase, snake_case, and path-based matching
"""
from __future__ import annotations
import re
from collections import defaultdict
from typing import Optional


def _split_camel_snake(name: str) -> list[str]:
    """Split name into camelCase/snake_case segments"""
    parts = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', name)
    parts = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', parts)
    parts = parts.replace('_', ' ')
    return [p for p in parts.split() if len(p) >= 1]


class FuzzySymbolSearcher:
    """
    Fuzzy symbol search engine.
    Matches queries against function/class names with:
    - CamelCase substring matching (e.g., "uS" matches "userService")
    - Snake_case prefix matching (e.g., "get_us" matches "get_user")
    - Path-based filtering (e.g., "services/user" narrows scope)
    """

    def __init__(self):
        self._symbols: list[dict] = []
        self._name_index: dict[str, list[int]] = defaultdict(list)
        self._path_index: dict[str, list[int]] = defaultdict(list)

    def build_index(self, chunks: list[dict]) -> None:
        """
        Build symbol index from chunks.
        Step 1: Extract named chunks (functions, classes)
        Step 2: Index by name substrings and path
        """
        self._symbols = []
        self._name_index = defaultdict(list)
        self._path_index = defaultdict(list)

        for i, chunk in enumerate(chunks):
            name = chunk.get('name', '')
            kind = chunk.get('kind', '')
            path = chunk.get('path', '')

            if not name or kind in {'section', 'export'}:
                continue

            symbol = {
                'id': chunk['id'],
                'name': name,
                'kind': kind,
                'path': path,
                'language': chunk.get('language', ''),
                'startLine': chunk.get('startLine', 0),
                'endLine': chunk.get('endLine', 0),
            }
            idx = len(self._symbols)
            self._symbols.append(symbol)

            # Index by lowercase name
            lower_name = name.lower()
            self._name_index[lower_name].append(idx)

            # Index by camelCase segments
            segments = _split_camel_snake(name)
            for seg in segments:
                if len(seg) >= 2:
                    self._name_index[seg.lower()].append(idx)

            # Index by path components
            path_parts = path.replace('\\', '/').split('/')
            for part in path_parts:
                if len(part) >= 2:
                    self._path_index[part.lower()].append(idx)

    def search(
        self,
        query: str,
        limit: int = 15,
        path_filter: Optional[str] = None,
        kind_filter: Optional[str] = None,
    ) -> list[dict]:
        """
        Fuzzy search for symbols matching query.
        Step 1: Parse query into name and path parts
        Step 2: Score each candidate symbol
        Step 3: Return top matches with metadata
        """
        if not query or not self._symbols:
            return []

        # Parse query: "path/name" or just "name"
        query_parts = query.replace('\\', '/').split('/')
        if len(query_parts) > 1:
            path_part = '/'.join(query_parts[:-1]).lower()
            name_part = query_parts[-1]
        else:
            path_part = ''
            name_part = query

        # Collect candidate indices
        candidates: set[int] = set()

        # Exact name match
        lower_name = name_part.lower()
        if lower_name in self._name_index:
            candidates.update(self._name_index[lower_name])

        # Prefix name match
        for key, indices in self._name_index.items():
            if key.startswith(lower_name) or lower_name.startswith(key):
                candidates.update(indices[:5])

        # CamelCase segment match
        query_segments = _split_camel_snake(name_part)
        for seg in query_segments:
            seg_lower = seg.lower()
            if seg_lower in self._name_index:
                candidates.update(self._name_index[seg_lower][:3])

        # If no candidates from name, try path
        if not candidates and path_part:
            for key, indices in self._path_index.items():
                if path_part in key or key in path_part:
                    candidates.update(indices[:5])

        # If still no candidates, do linear scan (for very fuzzy queries)
        if not candidates:
            for i, sym in enumerate(self._symbols):
                if lower_name in sym['name'].lower():
                    candidates.add(i)
                    if len(candidates) >= 50:
                        break

        # Score candidates
        scored = []
        for idx in candidates:
            sym = self._symbols[idx]

            # Apply filters
            if kind_filter and sym['kind'] != kind_filter:
                continue
            if path_filter and path_filter.lower() not in sym['path'].lower():
                continue

            score = _fuzzy_score(name_part, sym['name'])
            if path_part:
                path_score = _path_score(path_part, sym['path'])
                score = score * 0.7 + path_score * 0.3

            if score > 0:
                scored.append((score, sym))

        scored.sort(key=lambda x: -x[0])

        results = []
        for score, sym in scored[:limit]:
            results.append({
                **sym,
                'fuzzyScore': round(score, 3),
            })

        return results

    @property
    def symbol_count(self) -> int:
        return len(self._symbols)

    def to_dict(self) -> dict:
        """Serialize searcher state to a JSON-serializable dict"""
        return {
            'symbols': self._symbols,
            'name_index': {k: v for k, v in self._name_index.items()},
            'path_index': {k: v for k, v in self._path_index.items()},
            'symbol_count': len(self._symbols),
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'FuzzySymbolSearcher':
        """Restore searcher state from a serialized dict"""
        searcher = cls()
        searcher._symbols = list(data.get('symbols', []))
        searcher._name_index = defaultdict(list)
        for k, v in data.get('name_index', {}).items():
            searcher._name_index[k] = list(v)
        searcher._path_index = defaultdict(list)
        for k, v in data.get('path_index', {}).items():
            searcher._path_index[k] = list(v)
        return searcher


def _fuzzy_score(query: str, name: str) -> float:
    """
    Score fuzzy match between query and name.
    Higher = better match. Range [0, 1].
    """
    q = query.lower()
    n = name.lower()

    # Exact match
    if q == n:
        return 1.0

    # Prefix match
    if n.startswith(q):
        return 0.9 + 0.1 * (len(q) / len(n))

    # Substring match
    if q in n:
        pos = n.index(q) / max(len(n), 1)
        return 0.7 * (1.0 - pos * 0.3) * (len(q) / len(n))

    # CamelCase segment matching
    q_segments = _split_camel_snake(query)
    n_segments = _split_camel_snake(name)

    if q_segments and n_segments:
        matched = 0
        qi = 0
        for ns in n_segments:
            if qi < len(q_segments) and q_segments[qi].lower() in ns.lower():
                matched += 1
                qi += 1
        if matched > 0:
            coverage = matched / len(q_segments)
            return 0.5 * coverage

    # Character-by-character fuzzy match (subsequence)
    score = _subsequence_score(q, n)
    if score > 0:
        return 0.3 * score

    return 0.0


def _subsequence_score(query: str, text: str) -> float:
    """Check if query chars appear as subsequence in text"""
    qi = 0
    last_match_pos = -1
    gaps = 0

    for ti, tc in enumerate(text):
        if qi < len(query) and tc == query[qi]:
            if last_match_pos >= 0:
                gaps += ti - last_match_pos - 1
            last_match_pos = ti
            qi += 1

    if qi == len(query):
        # All chars matched; score based on coverage and compactness
        coverage = len(query) / max(len(text), 1)
        compactness = 1.0 / (1.0 + gaps * 0.1)
        return coverage * compactness

    return 0.0


def _path_score(query_path: str, actual_path: str) -> float:
    """Score path matching"""
    q_parts = query_path.split('/')
    a_parts = actual_path.replace('\\', '/').lower().split('/')

    matched = 0
    for qp in q_parts:
        for ap in a_parts:
            if qp in ap or ap in qp:
                matched += 1
                break

    return matched / max(len(q_parts), 1)
