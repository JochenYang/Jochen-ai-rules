# context-codebase/scripts/context_engine/search_ranking.py
"""
Hybrid search ranker — multi-stage code search inspired by CodeGraph.

Pipeline:
  1. Symbol extraction from query (CamelCase, snake_case, paths)
  2. Exact symbol name matching
  3. CamelCase boundary matching
  4. Compound term matching (2+ query terms in one symbol name)
  5. Co-location boosting
  6. Multi-signal fusion ranking
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict


# ---------------------------------------------------------------------------
# Token / symbol helpers
# ---------------------------------------------------------------------------

def _split_identifier(name: str) -> list[str]:
    """Split a CamelCase / snake_case / SCREAMING_SNAKE identifier into segments."""
    # CamelCase: "UserAuthService" -> "User", "Auth", "Service"
    parts = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', name)
    parts = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', parts)
    # snake_case / SCREAMING_SNAKE
    parts = parts.replace('_', ' ')
    return [p for p in parts.split() if len(p) >= 1]


def _extract_identifiers(text: str) -> list[str]:
    """Extract valid code identifiers from arbitrary text."""
    return re.findall(r'[A-Za-z_][A-Za-z0-9_]*', text)


def _extract_symbol_candidates(query: str) -> list[str]:
    """
    From a user query, extract all plausible symbol-name candidates.

    Examples:
      "user auth service"       -> ["user", "auth", "service"]
      "UserAuthService"         -> ["UserAuthService", "User", "Auth", "Service"]
      "user_auth_service"       -> ["user_auth_service", "user", "auth", "service"]
      "IAuthenticationProvider" -> ["IAuthenticationProvider", "Authentication", "Provider"]
    """
    candidates: list[str] = []

    # Whole tokens that look like identifiers
    for token in _extract_identifiers(query):
        normalized = token.strip()
        if not normalized or len(normalized) < 2:
            continue
        candidates.append(normalized)
        # Sub-segments from CamelCase / snake_case
        candidates.extend(
            seg for seg in _split_identifier(normalized) if len(seg) >= 2
        )

    # Deduplicate preserving order
    seen: set[str] = set()
    deduped: list[str] = []
    for c in candidates:
        key = c.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(c)
    return deduped


def _camel_case_prefix_match(token: str, symbol_name: str) -> bool:
    """Check if token matches a prefix of any segment in symbol_name's CamelCase split."""
    segments = _split_identifier(symbol_name)
    t_lower = token.lower()
    for seg in segments:
        if seg.lower().startswith(t_lower):
            return True
    return False


# ---------------------------------------------------------------------------
# HybridSearchRanker
# ---------------------------------------------------------------------------

class HybridSearchRanker:
    """
    Multi-stage search ranker that combines symbol-level and text-level signals.

    Accepts the same chunk list and metadata dicts as the existing
    ``retrieve_chunks()`` function, making it a drop-in enhancement.
    """

    def __init__(
        self,
        important_ranks: dict[str, int] | None = None,
        recent_changed: set[str] | None = None,
        file_dependency_map: dict[str, list[str]] | None = None,
    ):
        self.important_ranks = important_ranks or {}
        self.recent_changed = recent_changed or set()
        self.file_dependency_map = file_dependency_map or {}

    # ------------------------------------------------------------------ 
    # Public API
    # ------------------------------------------------------------------ 

    def rank(
        self,
        query: str,
        chunks: list[dict],
        task: str = "understand-project",
        limit: int = 10,
    ) -> list[dict]:
        """
        Rank chunks by relevance to *query* using the multi-stage pipeline.

        Returns a list of *limit* scored chunk dicts, ordered by descending
        score, each with an added ``rankingReasons`` list.
        """
        if not query or not query.strip():
            return []
        if not chunks:
            return []

        # Build an index on the fly (small — we operate over the same chunk list)
        chunk_by_id = {c["id"]: c for c in chunks}

        # ---- Stage 0: tokenise raw query for text signal ----
        raw_query_tokens = self._tokenize(query)
        query_symbols = _extract_symbol_candidates(query)

        # ---- Stage 1: score every chunk ----
        scored: list[tuple[float, str, list[str]]] = []

        for chunk in chunks:
            score, reasons = self._score_chunk(
                chunk, query, raw_query_tokens, query_symbols, task,
            )
            if score <= 0:
                continue
            scored.append((score, chunk["id"], reasons))

        if not scored:
            return []

        # ---- Stage 2: sort, deduplicate, enforce diversity ----
        scored.sort(key=lambda x: (-x[0], x[1]))

        selected: list[tuple[float, str, list[str]]] = []
        seen_ids: set[str] = set()
        file_counts: Counter[str] = Counter()
        max_per_file = max(1, int(limit * 0.30))  # at most 30 % from one file

        for score, chunk_id, reasons in scored:
            if chunk_id in seen_ids:
                continue
            chunk = chunk_by_id.get(chunk_id)
            if not chunk:
                continue
            path = chunk.get("path", "")

            # Per-file diversity cap
            if file_counts[path] >= max_per_file:
                continue
            # Test file cap (15 %)
            if limit > 3 and self._is_test_path(path) and file_counts["__test__"] >= max(1, int(limit * 0.15)):
                continue

            seen_ids.add(chunk_id)
            file_counts[path] += 1
            if self._is_test_path(path):
                file_counts["__test__"] += 1
            selected.append((score, chunk_id, reasons))
            if len(selected) >= limit:
                break

        # ---- Stage 3: format for consumer ----
        results: list[dict] = []
        for score, chunk_id, reasons in selected:
            chunk = chunk_by_id[chunk_id]
            results.append(self._format_result(chunk, round(score, 1), reasons))

        return results

    # ------------------------------------------------------------------ 
    # Scoring internals
    # ------------------------------------------------------------------ 

    _SIGNAL_WEIGHTS = {
        "exact_symbol_match": 80.0,
        "camel_case_prefix": 55.0,
        "compound_term_match": 60.0,
        "fts_match": 30.0,
        "keyword_overlap": 20.0,
        "co_location_boost": 15.0,
        "important_file": 12.0,
        "recent_change": 18.0,
        "task_relevance": 10.0,
    }

    def _score_chunk(
        self,
        chunk: dict,
        raw_query: str,
        raw_tokens: set[str],
        query_symbols: list[str],
        task: str,
    ) -> tuple[float, list[str]]:
        """
        Multi-signal score for a single chunk.

        Returns ``(score, [reason_strings])``.
        """
        score = 0.0
        reasons: list[str] = []
        path: str = chunk.get("path", "")
        name: str = chunk.get("name", "")
        kind: str = chunk.get("kind", "")
        signals: list[str] = chunk.get("signals", [])
        preview: str = chunk.get("preview", "")
        content: str = chunk.get("content", "")

        # ---- Signal A: exact symbol match ----
        for sym in query_symbols:
            if sym.lower() == name.lower():
                score += self._SIGNAL_WEIGHTS["exact_symbol_match"]
                reasons.append(f"exact symbol match: {sym}")
                break
        else:
            # ---- Signal B: CamelCase prefix match ----
            for sym in query_symbols:
                if _camel_case_prefix_match(sym, name):
                    score += self._SIGNAL_WEIGHTS["camel_case_prefix"]
                    reasons.append(f"camelCase prefix: {sym} -> {name}")
                    break
            else:
                # ---- Signal C: compound term match (2+ terms in same name) ----
                name_lower = name.lower()
                matched_terms = [
                    sym for sym in query_symbols
                    if len(sym) >= 3 and sym.lower() in name_lower
                ]
                if len(matched_terms) >= 2:
                    score += self._SIGNAL_WEIGHTS["compound_term_match"]
                    reasons.append(f"compound match: {', '.join(matched_terms)} in {name}")

        # ---- Signal D: FTS / keyword overlap ----
        haystack = " ".join([
            path, kind, name, " ".join(signals), preview, content,
        ]).lower()
        overlap = sorted(t for t in raw_tokens if t in haystack)
        overlap_count = len(overlap)
        token_count = max(len(raw_tokens), 1)
        if overlap_count:
            fts_score = overlap_count * 8
            # coverage bonus
            coverage = overlap_count / token_count
            fts_score += int(coverage * 15)
            score += fts_score
            reasons.append(f"keyword overlap: {', '.join(overlap[:4])}")
        elif token_count >= 3:
            # penalty for zero overlap on multi-word queries
            score -= 10
            reasons.append("low text overlap")

        # ---- Signal E: co-location boost ----
        # If the chunk's file path contains any query symbol as a component
        path_lower = path.lower()
        path_parts = set(re.split(r'[/\\]', path_lower))
        for sym in query_symbols:
            if sym.lower() in path_parts:
                score += self._SIGNAL_WEIGHTS["co_location_boost"]
                reasons.append(f"co-location: {sym} in path")
                break

        # ---- Signal F: important file boost ----
        path_rank = self.important_ranks.get(path)
        if path_rank is not None:
            boost = max(0, self._SIGNAL_WEIGHTS["important_file"] - path_rank)
            score += boost
            reasons.append("important file")

        # ---- Signal G: recent-change boost ----
        if path in self.recent_changed:
            if task in {"bugfix-investigation", "code-review"}:
                score += self._SIGNAL_WEIGHTS["recent_change"]
                reasons.append("recently changed")

        # ---- Signal H: task relevance ----
        if task == "understand-project" and kind in {"section", "model", "function"}:
            score += self._SIGNAL_WEIGHTS["task_relevance"]
            reasons.append("orientation chunk")
        elif task == "feature-delivery" and kind in {"route", "function", "model", "action-flow"}:
            score += self._SIGNAL_WEIGHTS["task_relevance"]
            reasons.append("implementation anchor")
        elif task == "bugfix-investigation" and kind in {"route", "function"}:
            score += self._SIGNAL_WEIGHTS["task_relevance"]
            reasons.append("execution path")
        elif task == "code-review" and kind in {"function", "model", "route"}:
            score += self._SIGNAL_WEIGHTS["task_relevance"]
            reasons.append("review hotspot")

        # ---- Test file down-rank ----
        if self._is_test_path(path):
            if task in {"feature-delivery", "understand-project", "onboarding"}:
                score -= 20
                reasons.append("test file downrank")

        return score, reasons

    # ------------------------------------------------------------------ 
    # Helpers
    # ------------------------------------------------------------------ 

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        """Simple tokenizer compatible with retrieval.py's tokenize()."""
        if not text:
            return set()
        text = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', text)
        text = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', text)
        STOPWORDS = {
            "the", "and", "for", "with", "from", "that", "this", "into", "when",
            "your", "have", "what", "where", "which", "does", "read", "code",
            "file", "files", "repo", "project", "understand", "task", "mode",
            "need", "use", "want",
        }
        return {
            t for t in re.findall(r"[A-Za-z][A-Za-z0-9_./-]*|[\u4e00-\u9fff]+|\d+", text.lower())
            if len(t) >= 2 and t not in STOPWORDS
        }

    @staticmethod
    def _is_test_path(path: str) -> bool:
        lowered = path.replace("\\", "/").lower()
        filename = lowered.rsplit("/", 1)[-1]
        test_indicators = {
            "/tests/", "/__tests__/", ".test.", ".spec.", ".e2e.", "_test.",
            "test-harness", "test_harness", "fixtures/",
        }
        return any(tok in lowered for tok in test_indicators) or filename.startswith(("test_", "spec_"))

    @staticmethod
    def _format_result(chunk: dict, score: float, reasons: list[str]) -> dict:
        return {
            "id": chunk.get("id", ""),
            "path": chunk.get("path", ""),
            "kind": chunk.get("kind", ""),
            "name": chunk.get("name", ""),
            "language": chunk.get("language", ""),
            "startLine": chunk.get("startLine", 0),
            "endLine": chunk.get("endLine", 0),
            "signals": chunk.get("signals", []),
            "preview": chunk.get("preview", ""),
            "score": score,
            "reasons": reasons,
        }
