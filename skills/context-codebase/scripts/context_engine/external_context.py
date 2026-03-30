from __future__ import annotations

import locale
import subprocess


def collect_external_context(project_path: str, file_records: list[dict]) -> dict:
    docs = sorted([
        record['path']
        for record in file_records
        if record['language'] == 'Markdown'
    ])
    design_docs = [path for path in docs if any(token in path.lower() for token in ['adr', 'design', 'plan', 'spec', 'decision'])]

    return {
        'recentCommits': collect_recent_commits(project_path),
        'recentChangedFiles': collect_recent_changed_files(project_path),
        'documentationSources': docs[:40],
        'decisionSources': design_docs[:20],
        'teamConventions': infer_conventions(file_records),
    }


def collect_recent_commits(project_path: str, limit: int = 8) -> list[dict]:
    stdout = run_git_command(
        project_path,
        [
            'git',
            'log',
            f'-{limit}',
            '--date=iso-strict',
            '--pretty=format:%H%x1f%ad%x1f%s',
        ],
    )
    if not stdout:
        return []

    commits = []
    for line in stdout.splitlines():
        parts = line.split('\x1f')
        if len(parts) != 3:
            continue
        commits.append({
            'hash': parts[0],
            'date': parts[1],
            'summary': parts[2],
        })
    return commits


def collect_recent_changed_files(project_path: str, limit: int = 20) -> list[str]:
    stdout = run_git_command(project_path, ['git', 'diff', '--name-only', 'HEAD~5..HEAD'])
    if not stdout:
        return []

    changed = []
    for line in stdout.splitlines():
        normalized = line.strip().replace('\\', '/')
        if normalized:
            changed.append(normalized)
        if len(changed) >= limit:
            break
    return changed


def infer_conventions(file_records: list[dict]) -> list[str]:
    conventions = []
    lower_paths = {record['path'].lower() for record in file_records}

    if any(path.endswith(('test_generate.py', '_test.py')) or '/tests/' in path for path in lower_paths):
        conventions.append('Tests are stored in dedicated test files or tests directories.')
    if any(path.endswith('README.md') for path in lower_paths):
        conventions.append('Repository documentation is anchored by root-level README files.')
    if any('/scripts/' in path for path in lower_paths):
        conventions.append('Automation and tooling are kept under scripts/ directories.')
    if any('/context_engine/' in path for path in lower_paths):
        conventions.append('Context-engine logic is isolated under scripts/context_engine/.')
    return conventions


def run_git_command(project_path: str, args: list[str]) -> str:
    try:
        completed = subprocess.run(
            args,
            cwd=project_path,
            capture_output=True,
            text=False,
            check=False,
        )
    except Exception:
        return ''

    if getattr(completed, 'returncode', 1) != 0:
        return ''

    return decode_subprocess_output(getattr(completed, 'stdout', b''))


def decode_subprocess_output(payload: bytes | bytearray | memoryview | str | None) -> str:
    if payload is None:
        return ''
    if isinstance(payload, str):
        return payload
    raw_payload = bytes(payload)

    encodings = []
    preferred = locale.getpreferredencoding(False)
    if preferred:
        encodings.append(preferred)
    encodings.extend(['utf-8', 'gb18030'])

    seen = set()
    for encoding in encodings:
        normalized = encoding.lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        try:
            return raw_payload.decode(encoding)
        except UnicodeDecodeError:
            continue

    return raw_payload.decode('utf-8', errors='replace')
