# context-codebase/scripts/context_engine/git_index.py
"""
Git integration index - blame, diff, and change frequency analysis.
Step 1: Collect git blame info for files
Step 2: Track change frequency (commit touch count)
Step 3: Identify hotspots (frequently changed files/modules)
Step 4: Extract recent diff context for bug-fix queries
"""
from __future__ import annotations
import os
import re
import subprocess
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

from .external_context import decode_subprocess_output


def _fetch_authors_for_file(project_path: str, path: str, since_days: int) -> tuple[str, list[dict]]:
    """Fetch recent authors for a single file (used for parallel execution)."""
    authors = _get_file_authors(project_path, path, since_days)
    return (path, authors)


def collect_git_stats(
    project_path: str,
    file_paths: list[str],
    max_blame_files: int = 50,
    since_days: int = 90,
    max_workers: int = 4,
) -> dict:
    """
    Collect comprehensive git statistics for the project.
    Step 1: Get change frequency per file
    Step 2: Get recent authors per file
    Step 3: Get blame info for top files
    Step 4: Identify hotspots and churn areas
    """
    result = {
        'changeFrequency': {},
        'recentAuthors': {},
        'hotspots': [],
        'churnFiles': [],
        'branchInfo': _get_branch_info(project_path),
    }

    # Change frequency (log --numstat)
    freq = _compute_change_frequency(project_path, since_days)
    result['changeFrequency'] = freq

    # Top hotspots: files with most changes
    sorted_freq = sorted(freq.items(), key=lambda x: -x[1])
    result['hotspots'] = [
        {'path': path, 'changes': count}
        for path, count in sorted_freq[:20]
    ]

    # Churn files: high insert+delete ratio
    churn = _compute_churn(project_path, since_days)
    result['churnFiles'] = [
        {'path': path, 'insertions': ins, 'deletions': dels}
        for path, (ins, dels) in sorted(churn.items(), key=lambda x: -(x[1][0] + x[1][1]))[:20]
    ]

    # Recent authors per file (for top changed files)
    # Threading: _get_file_authors is I/O-bound (subprocess calls), parallelize for speed
    paths_to_fetch = [path for path, _ in sorted_freq[:max_blame_files]]
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for path, authors in executor.map(
            lambda p: _fetch_authors_for_file(project_path, p, since_days),
            paths_to_fetch,
        ):
            if authors:
                result['recentAuthors'][path] = authors

    return result


def _compute_change_frequency(
    project_path: str, since_days: int,
) -> dict[str, int]:
    """Compute how many commits touched each file in the last N days"""
    try:
        output = _run_git(project_path, [
            'log', f'--since={since_days}.days', '--name-only', '--pretty=format:'
        ])
        if not output:
            return {}

        freq: Counter = Counter()
        for line in output.splitlines():
            line = line.strip()
            if line and not line.startswith('Merge'):
                freq[line] += 1

        return dict(freq)
    except Exception:
        return {}


def _compute_churn(
    project_path: str, since_days: int,
) -> dict[str, tuple[int, int]]:
    """Compute insertions and deletions per file (churn metric)"""
    try:
        output = _run_git(project_path, [
            'log', f'--since={since_days}.days', '--numstat', '--pretty=format:'
        ])
        if not output:
            return {}

        churn: dict[str, tuple[int, int]] = {}
        for line in output.splitlines():
            parts = line.split('\t')
            if len(parts) == 3:
                try:
                    ins = int(parts[0]) if parts[0] != '-' else 0
                    dels = int(parts[1]) if parts[1] != '-' else 0
                    path = parts[2]
                    old = churn.get(path, (0, 0))
                    churn[path] = (old[0] + ins, old[1] + dels)
                except ValueError:
                    continue

        return churn
    except Exception:
        return {}


def _get_file_authors(
    project_path: str, file_path: str, since_days: int,
) -> list[dict]:
    """Get recent authors for a specific file"""
    try:
        output = _run_git(project_path, [
            'log', f'--since={since_days}.days', '--format=%aN|%aE',
            '--', file_path
        ])
        if not output:
            return []

        authors = []
        seen = set()
        for line in output.splitlines():
            if '|' not in line:
                continue
            name, email = line.split('|', 1)
            if email not in seen:
                seen.add(email)
                authors.append({'name': name, 'email': email})

        return authors[:5]
    except Exception:
        return []


def _get_branch_info(project_path: str) -> dict:
    """Get current branch and remote info"""
    try:
        branch = _run_git(project_path, ['rev-parse', '--abbrev-ref', 'HEAD'])
        remote = _run_git(project_path, ['remote', 'get-url', 'origin']) \
            if _run_git(project_path, ['remote']) else ''

        return {
            'branch': branch.strip() if branch else '',
            'remote': remote.strip() if remote else '',
        }
    except Exception:
        return {}


def _run_git(project_path: str, args: list[str]) -> str:
    """Run a git command and return output"""
    try:
        result = subprocess.run(
            ['git'] + args,
            cwd=project_path,
            capture_output=True,
            timeout=10,
        )
        return decode_subprocess_output(result.stdout)
    except Exception:
        return ''


def get_file_blame(
    project_path: str, file_path: str,
) -> list[dict]:
    """
    Get git blame info for a file.
    Returns list of {line, commit, author, date} entries.
    """
    try:
        output = _run_git(project_path, [
            'blame', '--line-porcelain', '--', file_path
        ])
        if not output:
            return []

        entries = []
        current = {}
        for line in output.splitlines():
            if line.startswith('\t'):
                # Content line - save previous entry
                if current.get('commit'):
                    entries.append(current)
                current = {}
            elif ' ' in line:
                key = line.split(' ', 1)[0].replace('-', '_')
                value = line.split(' ', 1)[1] if ' ' in line else ''
                if key in ('commit', 'author', 'author_mail', 'author_time', 'summary'):
                    current[key] = value

        return entries[:100]  # Limit to first 100 entries
    except Exception:
        return []


def enrich_chunks_with_git(
    chunks: list[dict],
    git_stats: dict,
) -> list[dict]:
    """
    Enrich chunks with git metadata.
    Step 1: Add change frequency to each chunk
    Step 2: Add hotspot flag
    Step 3: Add churn score
    """
    change_freq = git_stats.get('changeFrequency', {})
    hotspot_paths = {h['path'] for h in git_stats.get('hotspots', [])}
    churn = git_stats.get('churnFiles', [])
    churn_map = {c['path']: c['insertions'] + c['deletions'] for c in churn}

    for chunk in chunks:
        path = chunk.get('path', '')
        freq = change_freq.get(path, 0)
        chunk['gitChangeFrequency'] = freq
        chunk['gitHotspot'] = path in hotspot_paths
        chunk['gitChurn'] = churn_map.get(path, 0)

    return chunks
