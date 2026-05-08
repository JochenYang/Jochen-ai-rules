#!/usr/bin/env python3
"""
context-codebase: Generate project snapshot JSON
Usage: python generate.py <project_path> [refresh|--refresh|read|--read|report|--report]
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import codecs
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from context_engine.analyzers import AnalyzerRegistry
from context_engine.csr import build_csr_read_enhancement
from context_engine.encoding_utils import decode_text_bytes, read_text_file_with_fallback
from context_engine.external_context import collect_external_context
from context_engine.graph import build_code_graph
from context_engine.retrieval import build_retrieval_artifacts, retrieve_chunks
from context_engine.semantic_chunker import SemanticChunker
from context_engine.chunk_tracker import ChunkTracker
from context_engine.sqlite_index import SQLiteIndex

from context_engine.fuzzy_search import FuzzySymbolSearcher
from context_engine.git_index import collect_git_stats, enrich_chunks_with_git

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None


from context_engine.config import *  # SNAPSHOT_VERSION = '3.0'
INDEX_STATE_VERSION = '1.0'
MAX_TEXT_FILE_BYTES = 512 * 1024
MAX_IMPORTANT_FILES = 15
MAX_REPRESENTATIVE_SNIPPETS = 5
MAX_SNIPPET_LINES = 12
MAX_CHUNK_LINES = 60
MAX_CHUNK_PREVIEW_LINES = 16
MAX_CHUNK_CATALOG_ITEMS = 40
HASH_AUDIT_BUDGET = 32
SKILL_NAME = 'context-codebase'
LEGACY_SKILL_NAMES = ['codebase-context', 'miloya-codebase']
SNAPSHOT_FILENAME = f'{SKILL_NAME}.json'
INDEX_STATE_FILENAME = f'{SKILL_NAME}.index.json'
SQLITE_FILENAME = f'{SKILL_NAME}.db'
LEGACY_SNAPSHOT_FILENAMES = [f'{legacy_name}.json' for legacy_name in LEGACY_SKILL_NAMES]
LEGACY_INDEX_STATE_FILENAMES = [f'{legacy_name}.index.json' for legacy_name in LEGACY_SKILL_NAMES]
LEGACY_SQLITE_FILENAMES = [f'{legacy_name}.db' for legacy_name in LEGACY_SKILL_NAMES]

EXCLUDE_DIRS = {
    'node_modules', '.git', 'dist', 'build', 'venv', '__pycache__',
    '.venv', 'env', '.env', 'coverage', '.next', '.nuxt', '.cache',
    '.svn', '.hg', 'vendor', 'target', 'out', '.idea', '.vscode',
    'site-packages', 'dist-packages', '.tox', '.nox', '.pytest_cache',
    '.mypy_cache', '.ruff_cache', '.hypothesis', '.eggs', '.yarn',
    '.pnpm-store', '.turbo', '.parcel-cache', '.sass-cache', '.gradle',
    '.terraform', '.serverless', '.aws-sam', '.docusaurus', '.expo',
    '.vercel', '.svelte-kit'
}

EXCLUDE_PATH_PREFIXES = {
    'repo/progress',
}

ENTRY_PATTERNS = [
    'index.ts', 'index.js', 'main.ts', 'main.js', 'app.ts', 'app.js',
    'App.tsx', 'App.ts', 'App.jsx', 'main.go', 'main.py', 'manage.py',
    'index.html', 'main.go', 'main.rs', 'Cargo.toml', 'go.mod'
]

FRAMEWORK_DEPS = {
    'react': 'React', 'react-dom': 'React',
    'next': 'Next.js',
    'vue': 'Vue',
    '@nestjs/core': 'NestJS',
    'express': 'Express',
    'fastapi': 'FastAPI',
    'flask': 'Flask',
    '@angular/core': 'Angular',
    'svelte': 'Svelte',
    'django': 'Django',
    'spring-boot-starter-web': 'Spring Boot',
    'gin-gonic/gin': 'Gin',
}

ARCHITECTURE_RULES = [
    ('all', ['controllers', 'routes'], 'MVC / Controller-based'),
    ('any', ['store', 'state', 'redux', 'zustand'], 'Flux / State management'),
    ('all', ['services', 'repositories'], 'Layered / Repository'),
    ('any', ['middleware'], 'Middleware-based'),
]

DEPENDENCY_FILES = {
    'package.json',
    'requirements.txt',
    'pyproject.toml',
    'go.mod',
    'Cargo.toml',
    'pom.xml',
}

MODULE_ROLE_HINTS = {
    'src': 'Primary application source code',
    'app': 'Application runtime and entry modules',
    'apps': 'Workspace applications in a monorepo',
    'packages': 'Shared packages in a monorepo',
    'components': 'UI components and presentation logic',
    'pages': 'Routable views or pages',
    'routes': 'HTTP or application routing definitions',
    'controllers': 'Request handlers and controller layer',
    'services': 'Business logic and orchestration',
    'repositories': 'Persistence and repository abstractions',
    'models': 'Data models and domain entities',
    'schemas': 'Schema definitions and validation',
    'store': 'State management',
    'state': 'State containers and reducers',
    'hooks': 'Reusable hooks and composition helpers',
    'utils': 'Utility helpers and shared functions',
    'lib': 'Reusable library code',
    'libs': 'Reusable library code',
    'api': 'API handlers and integration points',
    'scripts': 'Automation and maintenance scripts',
    'tests': 'Automated tests and fixtures',
    'docs': 'Project documentation and design notes',
    'config': 'Configuration files',
}

NOISY_QUERY_EXPANSION_TERMS = {
    'const', 'let', 'var', 'function', 'return', 'string', 'number', 'boolean',
    'array', 'object', 'type', 'types', 'value', 'values', 'item', 'items',
    'data', 'result', 'results', 'list', 'dict', 'map', 'set', 'module',
    'modules', 'file', 'files', 'path', 'paths', 'line', 'lines', 'class',
    'method', 'methods', 'param', 'params', 'argument', 'arguments',
}

LOW_SIGNAL_RETRIEVAL_TERMS = {
    'core', 'call', 'chain', 'entry', 'main', 'flow',
    'module', 'modules', 'handler', 'controller', 'service', 'router', 'route',
}

CODE_LIKE_EXTENSIONS = {
    '.py', '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs', '.go', '.rs', '.java',
    '.kt', '.swift', '.cs', '.php', '.rb', '.scala', '.lua', '.sh', '.ps1',
    '.json', '.yml', '.yaml', '.toml', '.ini', '.cfg', '.md', '.mdx',
}

SOURCE_EXTENSIONS = {'.py', '.js', '.jsx', '.ts', '.tsx'}
MONOREPO_MARKERS = {'pnpm-workspace.yaml', 'turbo.json', 'nx.json'}
IMPORTANT_FILE_NAMES = {
    'package.json', 'pyproject.toml', 'requirements.txt', 'go.mod',
    'Cargo.toml', 'pom.xml', 'README.md', 'README_zh.md', 'tsconfig.json',
    'vite.config.ts', 'vite.config.js', 'next.config.js', 'next.config.mjs',
}
ANALYZER_REGISTRY = AnalyzerRegistry(SCRIPT_DIR / 'context_engine' / 'ts_ast_bridge.js')


def normalize_rel_path(path: str) -> str:
    return path.replace('\\', '/')


def is_generated_env_dir(name: str) -> bool:
    normalized = (name or '').strip().lower()
    if not normalized:
        return False
    if normalized in EXCLUDE_DIRS:
        return True
    if re.fullmatch(r'(?:\.?venv|env)(?:[-_.]?\d+(?:\.\d+)*)?', normalized):
        return True
    if normalized.endswith('.egg-info'):
        return True
    return normalized.startswith('python') and normalized[6:].replace('.', '').isdigit()


def is_excluded_path(rel_path: str) -> bool:
    normalized = normalize_rel_path(rel_path).strip('./')
    if not normalized:
        return False

    parts = [part.strip().lower() for part in normalized.split('/') if part.strip()]
    if any(is_generated_env_dir(part) for part in parts):
        return True

    return any(
        normalized == prefix or normalized.startswith(prefix + '/')
        for prefix in EXCLUDE_PATH_PREFIXES
    )


def clean_content_for_parsing(content: str, ext: str) -> str:
    """Remove common comments to reduce regex false positives."""
    if ext == '.py':
        return re.sub(r'^\s*#.*$', '', content, flags=re.MULTILINE)

    if ext in ['.ts', '.tsx', '.js', '.jsx']:
        without_blocks = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        return re.sub(r'^\s*//.*$', '', without_blocks, flags=re.MULTILINE)

    return content


def extract_dependencies(project_path: str) -> dict[str, list[str]]:
    """Extract root-level dependency manifests for quick project understanding."""
    dependencies: dict[str, list[str]] = {}
    base = Path(project_path)

    pkg_path = base / 'package.json'
    if pkg_path.exists():
        try:
            with open(pkg_path, 'r', encoding='utf-8') as f:
                pkg = json.load(f)
            deps = {
                **pkg.get('dependencies', {}),
                **pkg.get('devDependencies', {}),
                **pkg.get('peerDependencies', {}),
            }
            if deps:
                dependencies['package.json'] = sorted(deps.keys())
        except Exception:
            pass

    requirements_path = base / 'requirements.txt'
    if requirements_path.exists():
        try:
            lines = []
            with open(requirements_path, 'r', encoding='utf-8') as f:
                for raw_line in f:
                    line = raw_line.strip()
                    if not line or line.startswith('#'):
                        continue
                    name = re.split(r'[<>=!~\[]', line, maxsplit=1)[0].strip()
                    if name:
                        lines.append(name)
            if lines:
                dependencies['requirements.txt'] = sorted(set(lines))
        except Exception:
            pass

    pyproject_path = base / 'pyproject.toml'
    if pyproject_path.exists():
        try:
            if tomllib is not None:
                data = tomllib.loads(pyproject_path.read_text(encoding='utf-8'))
                names = []
                for item in data.get('project', {}).get('dependencies', []):
                    name = re.split(r'[<>=!~\[]', item, maxsplit=1)[0].strip()
                    if name:
                        names.append(name)
                names.extend(
                    key for key in data.get('tool', {}).get('poetry', {}).get('dependencies', {}).keys()
                    if key != 'python'
                )
            else:
                content = pyproject_path.read_text(encoding='utf-8')
                names = re.findall(r'^\s*["\']?([A-Za-z0-9_.-]+)\s*[<>=!~]', content, flags=re.MULTILINE)
            if names:
                dependencies['pyproject.toml'] = sorted(set(names))
        except Exception:
            pass

    go_mod_path = base / 'go.mod'
    if go_mod_path.exists():
        try:
            content = go_mod_path.read_text(encoding='utf-8')
            names = re.findall(r'^\s*(?:require\s+)?([A-Za-z0-9_.\-/]+)\s+v', content, flags=re.MULTILINE)
            if names:
                dependencies['go.mod'] = sorted(set(names))
        except Exception:
            pass

    cargo_path = base / 'Cargo.toml'
    if cargo_path.exists():
        try:
            content = cargo_path.read_text(encoding='utf-8')
            section_match = re.search(r'\[dependencies\](.*?)(?:\n\[|$)', content, flags=re.DOTALL)
            if section_match:
                names = re.findall(r'^\s*([A-Za-z0-9_-]+)\s*=', section_match.group(1), flags=re.MULTILINE)
                if names:
                    dependencies['Cargo.toml'] = sorted(set(names))
        except Exception:
            pass

    pom_path = base / 'pom.xml'
    if pom_path.exists():
        try:
            content = pom_path.read_text(encoding='utf-8')
            names = re.findall(r'<artifactId>([^<]+)</artifactId>', content)
            if names:
                dependencies['pom.xml'] = sorted(set(names))
        except Exception:
            pass

    return dependencies


def summarize_modules(files: list[str], project_path: str) -> dict[str, str]:
    """Summarize top-level modules to provide higher-signal context."""
    module_files: dict[str, list[str]] = {}
    base = Path(project_path)

    for file_path in files:
        rel = normalize_rel_path(os.path.relpath(file_path, base))
        parts = Path(rel).parts
        module_key = './' if len(parts) == 1 else f'{parts[0]}/'
        module_files.setdefault(module_key, []).append(rel)

    summaries: dict[str, str] = {}
    for module_key, rel_paths in sorted(module_files.items()):
        if module_key == './':
            summaries[module_key] = (
                f'Project root metadata and entry files; {len(rel_paths)} files'
            )
            continue

        module_name = module_key.rstrip('/').split('/')[-1].lower()
        role = MODULE_ROLE_HINTS.get(module_name, 'Project module')
        notable_areas = sorted({
            part
            for rel_path in rel_paths
            for part in Path(rel_path).parts[1:3]
            if part and '.' not in part
        })[:3]

        summary = f'{role}; {len(rel_paths)} files'
        if notable_areas:
            summary += f'; notable areas: {", ".join(notable_areas)}'
        summaries[module_key] = summary

    return summaries


def rank_key_function(func: dict, entry_points: list[str]) -> tuple[int, int, str, int]:
    """Prioritize functions near important files for downstream consumers."""
    file_path = normalize_rel_path(func['file'])
    file_name = Path(file_path).name.lower()
    path_score = 0

    if file_path in entry_points:
        path_score -= 40
    if any(token in file_path.lower() for token in ['route', 'controller', 'service', 'api']):
        path_score -= 20
    if file_name.startswith(('main', 'app', 'index')):
        path_score -= 10
    if is_probably_test_path(file_path):
        path_score += 40
    if file_path.lower().endswith('.md'):
        path_score += 20

    return (path_score, func['line'], file_path, len(func['name']))


def infer_project_type(files: list[str], project_path: str, frameworks: list[str]) -> str:
    """Infer a readable project type for the summary."""
    base = Path(project_path)
    file_names = {Path(file_path).name for file_path in files}

    if any(marker in file_names for marker in MONOREPO_MARKERS):
        return 'Monorepo'
    if 'package.json' in file_names and any(name in frameworks for name in ['React', 'Next.js', 'Vue', 'Angular', 'Svelte']):
        return 'Frontend Application'
    if any(name in frameworks for name in ['Express', 'NestJS', 'FastAPI', 'Flask', 'Django', 'Spring Boot', 'Gin']):
        return 'Backend Service'
    if 'scripts' in {part for file_path in files for part in Path(normalize_rel_path(os.path.relpath(file_path, base))).parts[:-1]}:
        return 'Tooling / Automation'
    if (base / 'package.json').exists():
        return 'Node.js Project'
    if (base / 'pyproject.toml').exists() or (base / 'requirements.txt').exists():
        return 'Python Project'
    return 'unknown'


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def detect_language(path: str) -> str | None:
    return LANGUAGE_BY_EXTENSION.get(Path(path).suffix.lower())


LANGUAGE_BY_EXTENSION = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.jsx': 'JavaScript',
    '.ts': 'TypeScript',
    '.tsx': 'TypeScript',
    '.go': 'Go',
    '.rs': 'Rust',
    '.java': 'Java',
    '.json': 'JSON',
    '.md': 'Markdown',
    '.toml': 'TOML',
    '.yaml': 'YAML',
    '.yml': 'YAML',
    '.xml': 'XML',
}

TEXT_EXTENSIONS = set(LANGUAGE_BY_EXTENSION) | {'.txt', '.ini', '.cfg', '.conf', '.sh', '.ps1'}


def read_text_file(path: Path) -> str | None:
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        return None
    if path.stat().st_size > MAX_TEXT_FILE_BYTES:
        return None

    text, _encoding = read_text_file_with_fallback(path, max_bytes=MAX_TEXT_FILE_BYTES)
    return text


def compute_file_content_hash(path_obj: Path) -> str:
    digest = hashlib.sha256()
    with path_obj.open('rb') as file_obj:
        while True:
            chunk = file_obj.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def build_source_fingerprint(signatures: dict[str, dict]) -> str:
    digest = hashlib.sha256()

    for rel_path in sorted(signatures.keys()):
        meta = signatures[rel_path]
        digest.update(
            (
                f"{rel_path}:{meta.get('sizeBytes')}:{meta.get('mtimeNs')}:"
                f"{meta.get('contentHash', '')}\n"
            ).encode('utf-8')
        )

    return digest.hexdigest()


def build_fast_file_signatures(files: list[str], project_path: str) -> dict[str, dict]:
    base = Path(project_path)
    signatures = {}

    for file_path in files:
        path_obj = Path(file_path)
        rel_path = normalize_rel_path(os.path.relpath(file_path, base))
        stat = path_obj.stat()
        signatures[rel_path] = {
            'sizeBytes': stat.st_size,
            'mtimeNs': stat.st_mtime_ns,
        }

    return signatures


def fast_signature_matches(previous_meta: dict | None, current_meta: dict | None) -> bool:
    previous_meta = previous_meta or {}
    current_meta = current_meta or {}
    return {
        'sizeBytes': previous_meta.get('sizeBytes'),
        'mtimeNs': previous_meta.get('mtimeNs'),
    } == {
        'sizeBytes': current_meta.get('sizeBytes'),
        'mtimeNs': current_meta.get('mtimeNs'),
    }


def signature_matches(previous_meta: dict | None, current_meta: dict | None) -> bool:
    previous_meta = previous_meta or {}
    current_meta = current_meta or {}
    return {
        'sizeBytes': previous_meta.get('sizeBytes'),
        'mtimeNs': previous_meta.get('mtimeNs'),
        'contentHash': previous_meta.get('contentHash'),
    } == {
        'sizeBytes': current_meta.get('sizeBytes'),
        'mtimeNs': current_meta.get('mtimeNs'),
        'contentHash': current_meta.get('contentHash'),
    }


def build_file_signatures(
    files: list[str],
    project_path: str,
) -> dict[str, dict]:
    base = Path(project_path)
    fast_signatures = build_fast_file_signatures(files, project_path)
    signatures = {}

    for file_path in files:
        path_obj = Path(file_path)
        rel_path = normalize_rel_path(os.path.relpath(file_path, base))
        fast_meta = fast_signatures[rel_path]
        signatures[rel_path] = {
            **fast_meta,
            'contentHash': compute_file_content_hash(path_obj),
        }

    return signatures


def sanitize_git_path(path: str | None) -> str | None:
    normalized = normalize_rel_path((path or '').strip().strip('"'))
    if not normalized or is_excluded_path(normalized):
        return None
    return normalized


def collect_git_changed_paths(
    project_path: str,
    previous_commit: str | None = None,
    current_commit: str | None = None,
) -> set[str]:
    changed_paths: set[str] = set()

    for git_args in [
        ['diff', '--name-only', 'HEAD'],
        ['diff', '--cached', '--name-only', 'HEAD'],
        ['ls-files', '--others', '--exclude-standard'],
    ]:
        output = run_git_command(project_path, git_args)
        if not output:
            continue
        for raw_line in output.splitlines():
            sanitized = sanitize_git_path(raw_line)
            if sanitized:
                changed_paths.add(sanitized)

    status_output = run_git_command(project_path, ['status', '--porcelain'])
    if status_output:
        for raw_line in status_output.splitlines():
            line = raw_line.rstrip()
            if len(line) < 4:
                continue
            payload = line[3:]
            if ' -> ' in payload:
                old_path, new_path = payload.split(' -> ', 1)
                for candidate in (old_path, new_path):
                    sanitized = sanitize_git_path(candidate)
                    if sanitized:
                        changed_paths.add(sanitized)
            else:
                sanitized = sanitize_git_path(payload)
                if sanitized:
                    changed_paths.add(sanitized)

    if previous_commit and current_commit and previous_commit != current_commit:
        diff_output = run_git_command(project_path, ['diff', '--name-only', previous_commit, current_commit])
        if diff_output:
            for raw_line in diff_output.splitlines():
                sanitized = sanitize_git_path(raw_line)
                if sanitized:
                    changed_paths.add(sanitized)

    return changed_paths


def build_incremental_file_signatures(
    files: list[str],
    project_path: str,
    previous_files: dict[str, dict],
    previous_commit: str | None = None,
    current_commit: str | None = None,
    audit_cursor: int = 0,
) -> tuple[dict[str, dict], set[str], int]:
    base = Path(project_path)
    fast_signatures = build_fast_file_signatures(files, project_path)
    git_changed_paths = collect_git_changed_paths(project_path, previous_commit, current_commit)
    hash_candidate_paths = {
        path for path, fast_meta in fast_signatures.items()
        if path not in previous_files
        or not previous_files.get(path, {}).get('contentHash')
        or not fast_signature_matches(previous_files.get(path, {}), fast_meta)
        or path in git_changed_paths
    }

    if current_commit is None:
        stable_paths = sorted(
            path for path, fast_meta in fast_signatures.items()
            if path not in hash_candidate_paths
            and previous_files.get(path, {}).get('contentHash')
            and fast_signature_matches(previous_files.get(path, {}), fast_meta)
        )
        if stable_paths:
            normalized_cursor = audit_cursor % len(stable_paths)
            budget = min(HASH_AUDIT_BUDGET, len(stable_paths))
            audit_paths = [
                stable_paths[(normalized_cursor + offset) % len(stable_paths)]
                for offset in range(budget)
            ]
            hash_candidate_paths.update(audit_paths)
            next_audit_cursor = (normalized_cursor + budget) % len(stable_paths)
        else:
            next_audit_cursor = 0
    else:
        next_audit_cursor = 0

    signatures: dict[str, dict] = {}
    for rel_path, fast_meta in fast_signatures.items():
        previous_meta = previous_files.get(rel_path, {})
        if rel_path not in hash_candidate_paths and previous_meta.get('contentHash'):
            signatures[rel_path] = {
                **fast_meta,
                'contentHash': previous_meta['contentHash'],
            }
            continue

        signatures[rel_path] = {
            **fast_meta,
            'contentHash': compute_file_content_hash(base / rel_path),
        }

    return signatures, hash_candidate_paths, next_audit_cursor


def get_newest_source_mtime(files: list[str]) -> str | None:
    if not files:
        return None

    newest = max(Path(file_path).stat().st_mtime for file_path in files)
    return datetime.fromtimestamp(newest, tz=timezone.utc).replace(microsecond=0).isoformat()


def load_readme_summary(project_path: str) -> str | None:
    for file_name in ['README.md', 'README_zh.md']:
        path = Path(project_path) / file_name
        if not path.exists():
            continue

        content = read_text_file(path)
        if not content:
            continue

        for line in content.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                return stripped[:240]

    return None


def run_git_command(project_path: str, args: list[str]) -> str | None:
    try:
        completed = subprocess.run(
            ['git', *args],
            cwd=project_path,
            capture_output=True,
            text=False,
            check=False,
        )
    except Exception:
        return None

    if getattr(completed, 'returncode', 1) != 0:
        return None

    stdout, _encoding = decode_text_bytes(
        getattr(completed, 'stdout', b''),
        fallback_errors='replace',
    )
    if not stdout:
        return None
    return stdout.strip() or None


def collect_git_context(project_path: str) -> dict[str, str | None]:
    return {
        'branch': run_git_command(project_path, ['rev-parse', '--abbrev-ref', 'HEAD']),
        'commit': run_git_command(project_path, ['rev-parse', 'HEAD']),
        'status': 'dirty' if run_git_command(project_path, ['status', '--porcelain']) else 'clean',
    }


def extract_imports(content: str, language: str | None) -> list[str]:
    imports = []

    if language in ['TypeScript', 'JavaScript']:
        imports.extend(re.findall(r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]', content))
        imports.extend(re.findall(r'require\(\s*[\'"]([^\'"]+)[\'"]\s*\)', content))
    elif language == 'Python':
        imports.extend(re.findall(r'^\s*from\s+([A-Za-z0-9_\.]+)\s+import', content, flags=re.MULTILINE))
        imports.extend(re.findall(r'^\s*import\s+([A-Za-z0-9_\.]+)', content, flags=re.MULTILINE))

    return sorted(set(imports))[:8]


def extract_exports(content: str, language: str | None) -> list[str]:
    exports = []

    if language in ['TypeScript', 'JavaScript']:
        exports.extend(re.findall(r'export\s+(?:async\s+)?function\s+(\w+)', content))
        exports.extend(re.findall(r'export\s+class\s+(\w+)', content))
        exports.extend(re.findall(r'export\s+(?:const|let|var)\s+(\w+)', content))
        exports.extend(re.findall(r'export\s+interface\s+(\w+)', content))
        exports.extend(re.findall(r'export\s+type\s+(\w+)', content))
    elif language == 'Python':
        exports.extend(re.findall(r'^\s*def\s+([A-Za-z_]\w*)\s*\(', content, flags=re.MULTILINE))
        exports.extend(re.findall(r'^\s*class\s+([A-Za-z_]\w*)', content, flags=re.MULTILINE))

    return sorted(set(name for name in exports if not name.startswith('_')))[:8]


def _process_single_file(file_path: str, base: Path) -> tuple[dict | None, int]:
    """Process a single file record (used for parallel execution)."""
    try:
        path_obj = Path(file_path)
        rel_path = normalize_rel_path(os.path.relpath(file_path, base))
        language = detect_language(rel_path)
        file_stat = path_obj.stat()
        file_size = file_stat.st_size
        content, detected_encoding = read_text_file_with_fallback(
            path_obj,
            max_bytes=MAX_TEXT_FILE_BYTES,
        ) if path_obj.suffix.lower() in TEXT_EXTENSIONS else (None, None)
        line_count = len(content.splitlines()) if content is not None else 0
        analysis = ANALYZER_REGISTRY.analyze_file(content, rel_path, str(base))
        analysis_warnings = list(analysis.warnings)
        if (
            path_obj.suffix.lower() in TEXT_EXTENSIONS
            and file_size <= MAX_TEXT_FILE_BYTES
            and content is None
        ):
            analysis_warnings.append(
                'text decode failed; supported fallbacks: utf-8, utf-8-sig, locale preferred encoding, gb18030'
            )

        record = {
            'path': rel_path,
            'fileName': path_obj.name,
            'language': language,
            'lineCount': line_count,
            'sizeBytes': file_size,
            'content': content,
            'detectedEncoding': detected_encoding,
            'imports': analysis.imports,
            'exports': analysis.exports,
            'apiRoutes': analysis.api_routes,
            'dataModels': analysis.data_models,
            'keyFunctions': analysis.key_functions,
            'frameworkHints': analysis.framework_hints,
            'analysisEngine': analysis.engine,
            'analysisConfidence': analysis.confidence,
            'analysisWarnings': analysis_warnings,
        }
        return (record, line_count)
    except Exception:
        return (None, 0)


def collect_file_records(files: list[str], project_path: str) -> tuple[list[dict], int]:
    base = Path(project_path)
    records = []
    total_lines = 0

    # Threading: file I/O and analysis are I/O-bound, parallelize for speed
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(
            lambda fp: _process_single_file(fp, base),
            files,
        ))

    for record, line_count in results:
        if record is not None:
            records.append(record)
            total_lines += line_count

    return records, total_lines


def detect_workspace(file_records: list[dict], project_path: str, dependencies: dict[str, list[str]]) -> dict:
    project_name = Path(project_path).name
    packages = []

    manifest_records = [record for record in file_records if record['fileName'] in DEPENDENCY_FILES]
    for record in sorted(manifest_records, key=lambda item: item['path']):
        package_path = './' if '/' not in record['path'] else normalize_rel_path(str(Path(record['path']).parent)) + '/'
        role = 'root'
        for candidate in ['apps', 'packages', 'services', 'libs']:
            if package_path.startswith(candidate + '/'):
                role = candidate[:-1] if candidate.endswith('s') else candidate
                break

        package_name = project_name if package_path == './' else Path(package_path.rstrip('/')).name
        if record['fileName'] == 'package.json':
            try:
                pkg = json.loads((Path(project_path) / record['path']).read_text(encoding='utf-8'))
                package_name = pkg.get('name', package_name)
            except Exception:
                pass

        package_records = [
            item for item in file_records
            if item['path'] == record['path'] or package_path == './' or item['path'].startswith(package_path)
        ]
        entry_points = [
            item['path'] for item in package_records
            if item['fileName'] in ENTRY_PATTERNS
        ][:5]

        packages.append({
            'name': package_name,
            'path': package_path,
            'manifest': record['path'],
            'role': role,
            'entryPoints': entry_points,
            'dependencyCount': len(dependencies.get(record['path'], [])),
            'fileCount': len(package_records),
        })

    root_manifests = sorted([
        record['path'] for record in manifest_records
        if '/' not in record['path']
    ])
    is_monorepo = any(package['path'].startswith(('apps/', 'packages/')) for package in packages)

    return {
        'isMonorepo': is_monorepo,
        'rootManifests': root_manifests,
        'packages': packages,
    }


def infer_file_role(record: dict) -> str:
    path = record['path'].lower()
    file_name = record['fileName'].lower()

    if file_name in ['readme.md', 'readme_zh.md']:
        return 'Project overview'
    if file_name in DEPENDENCY_FILES:
        return 'Dependency manifest'
    if 'route' in path or 'controller' in path or record['apiRoutes']:
        return 'API surface'
    if 'service' in path:
        return 'Business logic'
    if 'model' in path or 'schema' in path or record['dataModels']:
        return 'Data model'
    if 'config' in path or file_name.endswith(('.json', '.toml')):
        return 'Configuration'
    if 'test' in path:
        return 'Test/support'
    if 'script' in path:
        return 'Automation'
    return 'Implementation'


def score_file(record: dict, entry_points: list[str], root_manifests: set[str]) -> tuple[int, list[str]]:
    score = 0
    reasons = []
    path = record['path']
    lower_path = path.lower()

    if path in entry_points:
        score += 110
        reasons.append('entry point')
    if record['fileName'] in IMPORTANT_FILE_NAMES:
        score += 90
        reasons.append('root/config manifest')
    if path in root_manifests:
        score += 80
        reasons.append('dependency manifest')
    if record['apiRoutes']:
        score += 60 + len(record['apiRoutes']) * 5
        reasons.append(f'{len(record["apiRoutes"])} API routes')
    if record['dataModels']:
        score += 45 + len(record['dataModels']) * 4
        reasons.append(f'{len(record["dataModels"])} data models')
    if record['exports']:
        score += 30 + len(record['exports']) * 2
        reasons.append(f'{len(record["exports"])} exports')
    if len(record['imports']) > 3:
        score += 10
        reasons.append('integration-heavy file')
    if record['keyFunctions']:
        score += min(30, len(record['keyFunctions']) * 2)
        reasons.append(f'{len(record["keyFunctions"])} named functions')
    if record['lineCount']:
        score += min(20, record['lineCount'] // 50)

    if any(token in lower_path for token in ['route', 'controller', 'service', 'model', 'schema', 'config', 'main', 'app', 'index']):
        score += 8

    if is_probably_test_path(lower_path):
        score -= 40
        reasons.append('test/support file')
    if lower_path.endswith('.md') and record['fileName'] not in ['README.md', 'README_zh.md']:
        score -= 15
        reasons.append('documentation file')

    return score, reasons


def build_important_files(file_records: list[dict], entry_points: list[str], workspace: dict) -> list[dict]:
    root_manifest_set = set(workspace.get('rootManifests', []))
    scored_files = []

    for record in file_records:
        score, reasons = score_file(record, entry_points, root_manifest_set)
        if score <= 0:
            continue
        scored_files.append((score, record, reasons))

    scored_files.sort(key=lambda item: (-item[0], item[1]['path']))
    important_files = []

    for score, record, reasons in scored_files[:MAX_IMPORTANT_FILES]:
        important_files.append({
            'path': record['path'],
            'role': infer_file_role(record),
            'language': record['language'],
            'lines': record['lineCount'],
            'imports': record['imports'],
            'exports': record['exports'],
            'score': score,
            'whyImportant': ', '.join(dict.fromkeys(reasons))[:220] or 'high-signal project file',
        })

    return important_files


def choose_anchor_line(record: dict) -> tuple[int, str]:
    content = record.get('content') or ''
    lines = content.splitlines()

    if record.get('language') == 'Markdown':
        for line_number, line in enumerate(lines, start=1):
            if line.strip() and not line.strip().startswith('#'):
                return line_number, 'document summary'
        return 1, 'document summary'

    patterns = [
        (r'router\.(get|post|put|delete|patch|head|options)\s*\(', 'route definition'),
        (r'^\s*@(Get|Post|Put|Delete|Patch|Head|Options)\s*\(', 'route decorator'),
        (r'^\s*@(app|router)\.(get|post|put|delete|patch)\s*\(', 'route decorator'),
        (r'(?:export\s+)?interface\s+\w+', 'data model'),
        (r'(?:export\s+)?class\s+\w+', 'class definition'),
        (r'export\s+(?:async\s+)?function\s+\w+', 'exported function'),
        (r'^\s*def\s+\w+\s*\(', 'function definition'),
        (r'^\s*class\s+\w+', 'class definition'),
    ]

    for line_number, line in enumerate(lines, start=1):
        for pattern, reason in patterns:
            if re.search(pattern, line):
                return line_number, reason

    for line_number, line in enumerate(lines, start=1):
        if line.strip():
            return line_number, 'file opening'

    return 1, 'file opening'


def build_representative_snippets(file_records: list[dict], important_files: list[dict]) -> list[dict]:
    record_map = {record['path']: record for record in file_records}
    snippets = []

    for important in important_files:
        record = record_map.get(important['path'])
        if not record or not record.get('content'):
            continue

        lines = record['content'].splitlines()
        if not lines:
            continue

        anchor_line, reason = choose_anchor_line(record)
        start = max(1, anchor_line - 2)
        end = min(len(lines), start + MAX_SNIPPET_LINES - 1)
        snippet = '\n'.join(lines[start - 1:end]).strip()
        if not snippet:
            continue

        snippets.append({
            'path': record['path'],
            'reason': reason,
            'startLine': start,
            'endLine': end,
            'snippet': snippet,
        })

        if len(snippets) >= MAX_REPRESENTATIVE_SNIPPETS:
            break

    return snippets


def build_context_hints(summary: dict, workspace: dict, important_files: list[dict], modules: dict[str, str]) -> dict:
    read_order = [item['path'] for item in important_files[:8]]

    return {
        'readOrder': read_order,
        'recommendedStart': read_order[0] if read_order else None,
        'highSignalAreas': list(modules.keys())[:5],
        'monorepo': workspace.get('isMonorepo', False),
        'description': summary.get('description'),
    }


def build_analysis_metadata(file_records: list[dict]) -> dict:
    engines_by_language = {}
    file_counts_by_engine = Counter()
    warnings = []

    for record in file_records:
        engine = record.get('analysisEngine') or 'none'
        file_counts_by_engine[engine] += 1
        language = record.get('language')
        if language and language not in engines_by_language and engine != 'none':
            engines_by_language[language] = engine
        warnings.extend(record.get('analysisWarnings', []))

    return {
        'engines': engines_by_language,
        'filesByEngine': dict(sorted(file_counts_by_engine.items())),
        'warnings': sorted(set(warnings)),
    }


def make_chunk_id(path: str, kind: str, start_line: int, end_line: int) -> str:
    digest = hashlib.sha1(f'{path}:{kind}:{start_line}:{end_line}'.encode('utf-8')).hexdigest()[:12]
    return f'{path}#{kind}:{start_line}-{end_line}:{digest}'


def clip_chunk_preview(lines: list[str], start_line: int, end_line: int) -> str:
    preview_end = min(end_line, start_line + MAX_CHUNK_PREVIEW_LINES - 1)
    return '\n'.join(lines[start_line - 1:preview_end]).strip()


def build_chunks(file_records: list[dict]) -> list[dict]:
    # Use semantic chunking when enabled
    if USE_SEMANTIC_CHUNKING:
        return build_chunks_semantic(file_records)

    chunks = []

    for record in file_records:
        content = record.get('content')
        if not content:
            continue

        lines = content.splitlines()
        if not lines:
            continue

        if record['language'] == 'Markdown':
            chunks.extend(build_markdown_chunks(record, lines))
            continue

        anchor_lines: list[tuple[int, str, list[str]]] = []
        for route in record.get('apiRoutes', []):
            line_no = route.get('line')
            if line_no:
                anchor_lines.append((line_no, 'route', [route.get('method', ''), route.get('path', '')]))
        for model in record.get('dataModels', []):
            line_no = model.get('line')
            if line_no:
                anchor_lines.append((line_no, 'model', [model.get('type', ''), model.get('name', '')]))
        for func in record.get('keyFunctions', []):
            if not isinstance(func, dict):
                continue
            line_no = func.get('line')
            name = func.get('name')
            if not isinstance(line_no, int) or line_no <= 0:
                continue
            if not isinstance(name, str) or not name.strip():
                continue
            anchor_lines.append((line_no, 'function', [name]))
        anchor_lines.extend(build_semantic_anchor_lines(record, lines))

        if anchor_lines:
            seen_ranges = set()
            for line_no, kind, signals in sorted(anchor_lines, key=lambda item: item[0]):
                start_line = max(1, line_no - 3)
                end_line = min(len(lines), start_line + MAX_CHUNK_LINES - 1)
                range_key = (start_line, end_line)
                if range_key in seen_ranges:
                    continue
                seen_ranges.add(range_key)
                chunks.append({
                    'id': make_chunk_id(record['path'], kind, start_line, end_line),
                    'path': record['path'],
                    'kind': kind,
                    'language': record['language'],
                    'startLine': start_line,
                    'endLine': end_line,
                    'signals': [signal for signal in signals if signal],
                    'preview': clip_chunk_preview(lines, start_line, end_line),
                    'analysisEngine': record.get('analysisEngine'),
                    'analysisConfidence': record.get('analysisConfidence'),
                })
            continue

        window_start = 1
        window_index = 0
        while window_start <= len(lines):
            window_end = min(len(lines), window_start + MAX_CHUNK_LINES - 1)
            chunks.append({
                'id': make_chunk_id(record['path'], f'window-{window_index}', window_start, window_end),
                'path': record['path'],
                'kind': 'window',
                'language': record['language'],
                'startLine': window_start,
                'endLine': window_end,
                'signals': [],
                'preview': clip_chunk_preview(lines, window_start, window_end),
                'analysisEngine': record.get('analysisEngine'),
                'analysisConfidence': record.get('analysisConfidence'),
            })
            window_index += 1
            window_start = window_end + 1

    return chunks


def build_chunks_semantic(file_records: list[dict]) -> list[dict]:
    """
    Semantic chunking using AST-aware SemanticChunker.
    Produces higher-quality chunks based on code structure.
    """
    chunks = []
    chunker = SemanticChunker()

    for record in file_records:
        content = record.get('content')
        if not content:
            continue

        # SemanticChunker uses lowercase language names
        raw_language = record.get('language')
        language = raw_language if isinstance(raw_language, str) and raw_language else 'unknown'
        lang_map = {
            'Python': 'python',
            'JavaScript': 'javascript',
            'TypeScript': 'typescript',
            'TSX': 'typescript',
            'JSX': 'javascript',
            'Go': 'go',
            'Rust': 'rust',
            'Java': 'java',
        }
        chunker_lang = lang_map.get(language, language.lower())

        try:
            semantic_chunks = chunker.chunk_file(content, record['path'], chunker_lang)
        except Exception:
            # Fallback to original behavior on error
            semantic_chunks = []

        for chunk in semantic_chunks:
            # Normalize to match original chunk format
            chunks.append({
                'id': chunk.get('id', make_chunk_id(record['path'], chunk.get('kind', 'section'), chunk.get('startLine', 1), chunk.get('endLine', 1))),
                'path': chunk.get('path', record['path']),
                'kind': chunk.get('kind', 'section'),
                'language': language,
                'startLine': chunk.get('startLine', 1),
                'endLine': chunk.get('endLine', 1),
                'signals': chunk.get('signals', []),
                'preview': chunk.get('preview', ''),
                'name': chunk.get('name', ''),
                'content': chunk.get('content', ''),
                'analysisEngine': record.get('analysisEngine'),
                'analysisConfidence': record.get('analysisConfidence'),
            })

    return chunks


def build_semantic_anchor_lines(record: dict, lines: list[str]) -> list[tuple[int, str, list[str]]]:
    language = record.get('language')
    if language not in {'TypeScript', 'JavaScript', 'TSX', 'JSX', 'Python'}:
        return []

    anchors: list[tuple[int, str, list[str]]] = []
    seen_lines = set()
    action_tokens = [
        'download',
        'install',
        'delete',
        'remove',
        'load',
        'sync',
        'start',
        'stop',
        'dispatch',
        'route',
        'reply',
        'send',
        'receive',
        'create',
        'update',
        'fetch',
        'clone',
        'import',
        'export',
        'connect',
        'select',
        'change',
        'choose',
        'toggle',
        'apply',
        'set',
    ]
    patterns = [
        (r'https?://', 'link', ['url', 'link']),
        (r'\bguideUrl\b|\b[A-Z0-9_]*GUIDE[A-Z0-9_]*\b', 'link', ['guide', 'url']),
        (r'\b(persistConfig|updateConfig|save\w*Config|set\w+Config)\b', 'config-flow', ['config', 'persist']),
        (r'\b(interface|type|class)\s+\w*Config\b', 'config-type', ['config', 'type']),
    ]

    def match_action_declaration(line: str) -> str | None:
        patterns = [
            r'^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\(',
            r'^\s*(?:export\s+)?(?:const|let|var)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:async\s+)?(?:\([^)]*\)|[A-Za-z_][A-Za-z0-9_]*)\s*=>',
            r'^\s*(?:export\s+)?(?:const|let|var)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:async\s+)?function\s*\(',
            r'^\s*(?:public\s+|private\s+|protected\s+|static\s+|async\s+)*(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\([^;]*\)\s*\{',
            r'^\s*(?:async\s+def|def)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\(',
        ]
        for pattern in patterns:
            matched = re.match(pattern, line)
            if not matched:
                continue
            name = matched.group('name').lower()
            if any(token in name for token in action_tokens):
                return name
        return None

    for line_number, line in enumerate(lines, start=1):
        if len(anchors) >= 12:
            break

        declaration_name = match_action_declaration(line)
        if declaration_name and line_number not in seen_lines:
            seen_lines.add(line_number)
            action = next((token for token in action_tokens if token in declaration_name), 'operation')
            anchors.append((line_number, 'action-flow', [action, 'operation']))

        for pattern, kind, signals in patterns:
            if re.search(pattern, line):
                if line_number in seen_lines:
                    break
                seen_lines.add(line_number)
                anchors.append((line_number, kind, signals))
                break

    return anchors


def build_markdown_chunks(record: dict, lines: list[str]) -> list[dict]:
    chunks = []
    heading_indexes = [
        index + 1
        for index, line in enumerate(lines)
        if line.strip().startswith('#')
    ]

    if not heading_indexes:
        return [{
            'id': make_chunk_id(record['path'], 'document', 1, min(len(lines), MAX_CHUNK_LINES)),
            'path': record['path'],
            'kind': 'document',
            'language': record['language'],
            'startLine': 1,
            'endLine': min(len(lines), MAX_CHUNK_LINES),
            'signals': ['documentation'],
            'preview': clip_chunk_preview(lines, 1, min(len(lines), MAX_CHUNK_LINES)),
            'analysisEngine': record.get('analysisEngine'),
            'analysisConfidence': record.get('analysisConfidence'),
        }]

    for index, start_line in enumerate(heading_indexes):
        next_heading = heading_indexes[index + 1] - 1 if index + 1 < len(heading_indexes) else len(lines)
        end_line = min(next_heading, start_line + MAX_CHUNK_LINES - 1)
        heading = lines[start_line - 1].strip().lstrip('#').strip()
        chunks.append({
            'id': make_chunk_id(record['path'], 'section', start_line, end_line),
            'path': record['path'],
            'kind': 'section',
            'language': record['language'],
            'startLine': start_line,
            'endLine': end_line,
            'signals': [heading] if heading else ['documentation'],
            'preview': clip_chunk_preview(lines, start_line, end_line),
            'analysisEngine': record.get('analysisEngine'),
            'analysisConfidence': record.get('analysisConfidence'),
        })

    return chunks


def load_existing_index_state(index_state_file: Path) -> dict | None:
    if not index_state_file.exists():
        return None

    try:
        return json.loads(index_state_file.read_text(encoding='utf-8'))
    except Exception:
        return None


def resolve_progress_artifact(progress_dir: Path, preferred_name: str, legacy_names: list[str]) -> Path:
    preferred_path = progress_dir / preferred_name
    if preferred_path.exists():
        return preferred_path

    for legacy_name in legacy_names:
        legacy_path = progress_dir / legacy_name
        if legacy_path.exists():
            return legacy_path

    return preferred_path


def resolve_snapshot_file(progress_dir: Path) -> Path:
    return resolve_progress_artifact(progress_dir, SNAPSHOT_FILENAME, LEGACY_SNAPSHOT_FILENAMES)


def resolve_index_state_file(progress_dir: Path) -> Path:
    return resolve_progress_artifact(progress_dir, INDEX_STATE_FILENAME, LEGACY_INDEX_STATE_FILENAMES)


def resolve_sqlite_file(progress_dir: Path) -> Path:
    return resolve_progress_artifact(progress_dir, SQLITE_FILENAME, LEGACY_SQLITE_FILENAMES)


def diff_index_state(previous_state: dict | None, current_signatures: dict[str, dict]) -> dict:
    previous_files = (previous_state or {}).get('files', {})
    previous_paths = set(previous_files.keys())
    current_paths = set(current_signatures.keys())

    new_paths = current_paths - previous_paths
    removed_paths = previous_paths - current_paths
    shared_paths = current_paths & previous_paths
    changed_paths = {
        path for path in shared_paths
        if not signature_matches(previous_files.get(path, {}), current_signatures.get(path, {}))
    }
    unchanged_paths = shared_paths - changed_paths

    return {
        'newFiles': len(new_paths),
        'changedFiles': len(changed_paths),
        'removedFiles': len(removed_paths),
        'unchangedFiles': len(unchanged_paths),
    }


def build_chunk_catalog(chunks: list[dict], important_files: list[dict]) -> list[dict]:
    important_paths = {item['path']: index for index, item in enumerate(important_files)}

    ranked_chunks = sorted(
        chunks,
        key=lambda item: (
            important_paths.get(item['path'], 999),
            0 if item['kind'] in {'route', 'model', 'function', 'section'} else 1,
            item['path'],
            item['startLine'],
        ),
    )

    catalog = []
    for chunk in ranked_chunks[:MAX_CHUNK_CATALOG_ITEMS]:
        catalog.append({
            'id': chunk['id'],
            'path': chunk['path'],
            'kind': chunk['kind'],
            'language': chunk['language'],
            'startLine': chunk['startLine'],
            'endLine': chunk['endLine'],
            'signals': chunk['signals'],
            'preview': chunk['preview'],
        })
    return catalog


def build_index_metadata(
    base: Path,
    index_state_file: Path,
    previous_state: dict | None,
    current_signatures: dict[str, dict],
    chunks: list[dict],
    reusing_snapshot: bool,
) -> dict:
    delta = diff_index_state(previous_state, current_signatures)
    return {
        'stateVersion': INDEX_STATE_VERSION,
        'statePath': normalize_rel_path(str(index_state_file.relative_to(base))),
        'fileCount': len(current_signatures),
        'chunkCount': len(chunks),
        'reusedSnapshot': reusing_snapshot,
        'delta': delta,
    }


def build_index_files_payload(
    current_signatures: dict[str, dict],
    chunks: list[dict],
    file_records: list[dict],
) -> dict[str, dict]:
    chunk_ids_by_path: dict[str, list[str]] = {}
    for chunk in chunks:
        chunk_ids_by_path.setdefault(chunk['path'], []).append(chunk['id'])

    files_payload = {}
    for record in file_records:
        files_payload[record['path']] = {
            **current_signatures.get(record['path'], {}),
            'language': record['language'],
            'lineCount': record['lineCount'],
            'analysisEngine': record.get('analysisEngine'),
            'analysisConfidence': record.get('analysisConfidence'),
            'chunkIds': chunk_ids_by_path.get(record['path'], []),
        }
    return files_payload


def save_index_state_payload(index_state_file: Path, payload: dict) -> None:
    index_state_file.parent.mkdir(parents=True, exist_ok=True)
    index_state_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')


def save_index_state(
    index_state_file: Path,
    current_signatures: dict[str, dict],
    chunks: list[dict],
    file_records: list[dict],
    source_fingerprint: str,
) -> None:
    global USE_INCREMENTAL_MODE
    payload = {
        'version': INDEX_STATE_VERSION,
        'generatedAt': utc_now_iso(),
        'sourceFingerprint': source_fingerprint,
        'files': build_index_files_payload(current_signatures, chunks, file_records),
        'chunks': chunks,
    }

    # Add incremental tracking when enabled
    if USE_INCREMENTAL_MODE:
        try:
            tracker = ChunkTracker()
            existing_index_state = load_existing_index_state(index_state_file)

            if existing_index_state and 'chunkStates' in existing_index_state:
                # Load old chunk states
                old_states = {}
                for chunk_id, state_data in existing_index_state.get('chunkStates', {}).items():
                    from context_engine.chunk_tracker import ChunkState
                    old_states[chunk_id] = ChunkState(
                        chunk_id=state_data['chunk_id'],
                        content_hash=state_data['content_hash'],
                        version=state_data.get('version', 1)
                    )

                # Track new chunks
                new_states = tracker.track(chunks)

                # Merge states with version tracking
                merged_states = tracker.merge_states(old_states, new_states)

                # Add change set info to payload
                change_set = tracker.diff(old_states, new_states)
                payload['_incremental'] = {
                    'added': len(change_set.added),
                    'modified': len(change_set.modified),
                    'deleted': len(change_set.deleted),
                    'unchanged': len(change_set.unchanged),
                }

                # Convert merged states back to dict format for JSON serialization
                payload['chunkStates'] = {
                    chunk_id: {
                        'chunk_id': state.chunk_id,
                        'content_hash': state.content_hash,
                        'version': state.version
                    }
                    for chunk_id, state in merged_states.items()
                }
            else:
                # First run - initialize chunk states
                new_states = tracker.track(chunks)
                payload['chunkStates'] = {
                    chunk_id: {
                        'chunk_id': state.chunk_id,
                        'content_hash': state.content_hash,
                        'version': state.version
                    }
                    for chunk_id, state in new_states.items()
                }
        except Exception:
            print(f'WARNING: ChunkTracker failed, disabling incremental mode')
            USE_INCREMENTAL_MODE = False

    save_index_state_payload(index_state_file, payload)


def load_existing_snapshot(output_file: Path) -> dict | None:
    if not output_file.exists():
        return None

    try:
        return json.loads(output_file.read_text(encoding='utf-8'))
    except Exception:
        return None


def write_snapshot(output_file: Path, snapshot: dict, chunks: list[dict] | None = None) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding='utf-8')

    # Write to SQLite index when enabled
    if USE_SQLITE_INDEX:
        try:
            db_path = str(output_file.parent / SQLITE_FILENAME)
            sqlite_index = SQLiteIndex(db_path)

            sqlite_chunks = chunks if chunks is not None else snapshot.get('chunks', [])
            if sqlite_chunks:
                print(f'  writing {len(sqlite_chunks):,} chunks to FTS5 index...', file=sys.stderr)
                # Normalize chunk format for SQLiteIndex
                normalized_chunks = []
                for chunk in sqlite_chunks:
                    normalized_chunks.append({
                        'id': chunk.get('id', ''),
                        'path': chunk.get('path', ''),
                        'startLine': chunk.get('startLine'),
                        'endLine': chunk.get('endLine'),
                        'kind': chunk.get('kind', ''),
                        'name': chunk.get('name', ''),
                        'language': chunk.get('language', ''),
                        'signals': chunk.get('signals', []),
                        'preview': chunk.get('preview', ''),
                    })
                sqlite_index.upsert_chunks(normalized_chunks)

                # Delete stale chunks (not in current snapshot)
                print(f'  cleaning stale chunks...', file=sys.stderr)
                valid_ids = {chunk['id'] for chunk in sqlite_chunks if chunk.get('id')}
                sqlite_index.delete_stale(valid_ids)

            sqlite_index.close()
        except Exception as exc:
            print(
                f'WARNING: SQLiteIndex failed, snapshot written without index update: {exc}',
                file=sys.stderr,
            )


def summarize_modules_from_records(file_records: list[dict]) -> dict[str, str]:
    module_stats = {}

    for record in file_records:
        parts = Path(record['path']).parts
        module_key = './' if len(parts) == 1 else f'{parts[0]}/'
        stats = module_stats.setdefault(module_key, {
            'files': 0,
            'lines': 0,
            'routes': 0,
            'models': 0,
            'functions': 0,
            'languages': Counter(),
            'areas': set(),
        })

        stats['files'] += 1
        stats['lines'] += record['lineCount']
        stats['routes'] += len(record['apiRoutes'])
        stats['models'] += len(record['dataModels'])
        stats['functions'] += len(record['keyFunctions'])
        if record['language']:
            stats['languages'][record['language']] += 1
        for part in parts[1:3]:
            if '.' not in part:
                stats['areas'].add(part)

    summaries = {}
    for module_key, stats in sorted(module_stats.items()):
        if module_key == './':
            summaries[module_key] = (
                f'Project root metadata and entry files; {stats["files"]} files; '
                f'{stats["lines"]} lines'
            )
            continue

        module_name = module_key.rstrip('/').split('/')[-1].lower()
        role = MODULE_ROLE_HINTS.get(module_name, 'Project module')
        primary_language = stats['languages'].most_common(1)[0][0] if stats['languages'] else 'mixed'
        summary = (
            f'{role}; {stats["files"]} files; {stats["lines"]} lines; '
            f'primary language: {primary_language}'
        )
        if stats['routes']:
            summary += f'; routes: {stats["routes"]}'
        if stats['models']:
            summary += f'; models: {stats["models"]}'
        if stats['functions']:
            summary += f'; functions: {stats["functions"]}'
        if stats['areas']:
            summary += f'; notable areas: {", ".join(sorted(stats["areas"])[:3])}'
        summaries[module_key] = summary

    return summaries


def build_summary(
    project_path: str,
    files: list[str],
    frameworks: list[str],
    entry_points: list[str],
    total_lines: int,
    file_records: list[dict],
    important_files: list[dict],
) -> dict:
    pkg_path = Path(project_path) / 'package.json'
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text(encoding='utf-8'))
            project_name = pkg.get('name', Path(project_path).name)
        except Exception:
            project_name = Path(project_path).name
    else:
        project_name = Path(project_path).name

    language_counter = Counter(record['language'] for record in file_records if record['language'])
    dominant_languages = [
        {'language': language, 'files': count}
        for language, count in language_counter.most_common(5)
    ]

    return {
        'name': project_name,
        'type': infer_project_type(files, project_path, frameworks),
        'description': load_readme_summary(project_path),
        'techStack': frameworks,
        'entryPoints': entry_points,
        'totalFiles': len(files),
        'totalLines': total_lines,
        'dominantLanguages': dominant_languages,
        'importantPaths': [item['path'] for item in important_files[:8]],
    }


def build_focus_context_pack(
    query: str,
    task: str,
    snapshot: dict,
    index_state: dict | None,
    sqlite_db_path: str | None = None,
) -> dict | None:
    if not query:
        return None

    index_state = index_state or {}

    graph = snapshot.get('graph', {})
    important_files = snapshot.get('importantFiles', [])
    external_context = snapshot.get('externalContext', {})
    important_ranks = {item['path']: index for index, item in enumerate(important_files)}
    recent_changed = set(external_context.get('recentChangedFiles', []))
    query_intent = enrich_query_intent_with_snapshot(snapshot, infer_query_intent(query))
    read_profile = select_read_profile(query_intent)
    expanded_query_terms = expand_query_terms_for_retrieval(
        query_intent,
        snapshot.get('retrieval', {}),
    )
    expanded_query = ' '.join(expanded_query_terms) or query
    chunks, retrieval_diagnostics = load_sqlite_query_chunks(sqlite_db_path, query, expanded_query_terms)
    if not chunks:
        chunks = index_state.get('chunks', [])
        if chunks:
            retrieval_diagnostics = {
                **retrieval_diagnostics,
                'backend': 'index-json',
                'fallbackUsed': retrieval_diagnostics.get('sqliteAvailable', False),
                'jsonChunkCount': len(chunks),
            }
    if not chunks:
        return None
    file_dependency_map = {
        item['path']: item['dependsOn']
        for item in graph.get('fileDependencies', [])
    }
    matches = retrieve_chunks(
        query=expanded_query,
        chunks=chunks,
        important_ranks=important_ranks,
        recent_changed=recent_changed,
        file_dependency_map=file_dependency_map,
        task=task,
        limit=36,
    )
    matches = rerank_read_matches(matches, query_intent, read_profile)
    matches = prioritize_matches_by_coverage(matches, query_intent, min_coverage=0.2)[:14]
    related_paths = []
    for match in matches:
        related_paths.append(match['path'])
        related_paths.extend(file_dependency_map.get(match['path'], []))

    return {
        'task': task,
        'query': query,
        'matches': matches,
        'files': list(dict.fromkeys(related_paths))[:12],
        'retrievalDiagnostics': retrieval_diagnostics,
    }


def expand_query_terms_for_retrieval(query_intent: dict, retrieval: dict) -> list[str]:
    base_terms = list(dict.fromkeys([
        *query_intent.get('terms', []),
        *query_intent.get('keywords', []),
    ]))
    if len(base_terms) >= 3:
        return base_terms[:36]

    expanded_terms = list(base_terms)
    related_terms = (retrieval.get('projectVocabulary') or {}).get('relatedTerms', {})

    for term in list(base_terms)[:12]:
        additions = 0
        for related in related_terms.get(term.lower(), [])[:6]:
            normalized = related.strip().lower()
            if not normalized or normalized in expanded_terms:
                continue
            if not should_keep_related_expansion(term, normalized):
                continue
            expanded_terms.append(normalized)
            additions += 1
            if additions >= 2:
                break

    return expanded_terms[:36]


def load_sqlite_query_chunks(
    sqlite_db_path: str | None,
    query: str,
    expanded_query_terms: list[str],
    limit: int = 36,
) -> tuple[list[dict], dict]:
    diagnostics = {
        'backend': 'none',
        'sqliteEnabled': bool(sqlite_db_path),
        'sqliteAvailable': False,
        'sqliteHitCount': 0,
        'fallbackUsed': False,
        'jsonChunkCount': 0,
    }
    if not sqlite_db_path:
        return [], diagnostics

    db_path = Path(sqlite_db_path)
    if not db_path.exists():
        return [], diagnostics
    diagnostics['sqliteAvailable'] = True

    query_terms = []
    normalized_query = normalize_query_text(query)
    if normalized_query:
        query_terms.append(normalized_query)
    query_terms.extend(term.strip() for term in expanded_query_terms if term and term.strip())

    deduped_terms = []
    seen_terms = set()
    for term in query_terms:
        lowered = term.lower()
        if len(lowered) < 2 or lowered in seen_terms:
            continue
        seen_terms.add(lowered)
        deduped_terms.append(term)

    if not deduped_terms:
        return [], diagnostics

    prioritized_terms: list[str] = []
    deferred_terms: list[str] = []
    for term in deduped_terms:
        lowered = term.lower()
        if len(deduped_terms) >= 3 and lowered in LOW_SIGNAL_RETRIEVAL_TERMS:
            deferred_terms.append(term)
            continue
        prioritized_terms.append(term)
    ordered_terms = prioritized_terms + deferred_terms

    collected: dict[str, dict] = {}

    try:
        sqlite_index = SQLiteIndex(str(db_path))
        for term in ordered_terms[:12]:
            for chunk in sqlite_index.search(term, limit=limit):
                chunk_id = chunk.get('id')
                if not chunk_id or chunk_id in collected:
                    continue
                collected[chunk_id] = chunk
                if len(collected) >= limit * 3:
                    diagnostics['backend'] = 'sqlite'
                    diagnostics['sqliteHitCount'] = len(collected)
                    return list(collected.values()), diagnostics
    except Exception:
        return [], diagnostics

    if collected:
        diagnostics['backend'] = 'sqlite'
        diagnostics['sqliteHitCount'] = len(collected)
    return list(collected.values()), diagnostics


def build_read_payload(
    snapshot: dict,
    index_state: dict | None,
    task: str,
    query: str | None,
    sqlite_db_path: str | None = None,
) -> dict:
    normalized_query = normalize_query_text(query)
    retrieval = snapshot.get('retrieval', {})
    available_tasks = retrieval.get('availableTasks', [])
    base_query_intent = infer_query_intent(normalized_query)
    selected_task = resolve_read_task(task, available_tasks, retrieval, base_query_intent)
    quick_start = snapshot.get('contextHints', {})
    graph = snapshot.get('graph', {})
    important_files = snapshot.get('importantFiles', [])
    representative_snippets = snapshot.get('representativeSnippets', [])
    try:
        csr_context = build_csr_read_enhancement(
            snapshot,
            index_state,
            selected_task,
            normalized_query,
            base_query_intent,
        )
    except Exception:
        csr_context = {}
    query_intent = enrich_query_intent_with_snapshot(
        snapshot,
        merge_query_intent(base_query_intent, csr_context),
    )
    read_profile = select_read_profile(query_intent)
    hinted_file_paths = collect_hint_file_paths(index_state, query_intent, read_profile)
    read_limits = determine_read_limits(query_intent)
    retrieval_diagnostics = {
        'backend': 'context-pack',
        'sqliteEnabled': bool(sqlite_db_path),
        'sqliteAvailable': bool(sqlite_db_path and Path(sqlite_db_path).exists()),
        'sqliteHitCount': 0,
        'fallbackUsed': False,
        'jsonChunkCount': len((index_state or {}).get('chunks', [])),
    }

    if normalized_query:
        focus_pack = build_focus_context_pack(
            normalized_query,
            selected_task,
            snapshot,
            index_state,
            sqlite_db_path=sqlite_db_path,
        )
        snippet_items = (focus_pack or {}).get('matches', [])
        file_paths = (focus_pack or {}).get('files', [])
        task_description = describe_task(snapshot, selected_task)
        retrieval_diagnostics = (focus_pack or {}).get('retrievalDiagnostics', retrieval_diagnostics)
    else:
        task_pack = snapshot.get('contextPacks', {}).get(selected_task, {})
        snippet_items = task_pack.get('chunks', [])
        file_paths = build_default_read_paths(snapshot, task_pack)
        task_description = task_pack.get('description') or describe_task(snapshot, selected_task)

    snippet_items = blend_match_sources(
        csr_context.get('matches', []),
        snippet_items,
        query_intent,
    )
    file_paths = merge_ordered_paths(file_paths, csr_context.get('files', []))
    file_paths = merge_ordered_paths(file_paths, hinted_file_paths)
    snippet_items = rerank_read_matches(snippet_items, query_intent, read_profile)
    snippet_items = prioritize_matches_by_coverage(snippet_items, query_intent)
    file_paths = prioritize_read_file_paths(file_paths, snippet_items, query_intent, read_profile)
    file_paths = prioritize_files_by_coverage(file_paths, snippet_items, query_intent)
    file_paths = refine_read_file_paths(snapshot, file_paths, query_intent, read_profile)
    search_scope = merge_search_scope(
        build_read_search_scope(snapshot, file_paths[:read_limits['files']]),
        csr_context,
    )
    ranking_diagnostics = build_ranking_diagnostics(
        snippet_items,
        file_paths,
        query_intent,
        csr_context,
        topk_snippets=read_limits['snippets'],
        topk_files=read_limits['files'],
    )

    return {
        'mode': 'read',
        'responseMode': 'lightweight',
        'packVersion': '1.0',
        'task': selected_task,
        'query': normalized_query,
        'snapshotPath': snapshot.get('freshness', {}).get('snapshotPath'),
        'sourceFingerprint': snapshot.get('sourceFingerprint'),
        'freshness': snapshot.get('freshness'),
        'analysis': snapshot.get('analysis'),
        'quickStart': {
            'recommendedStart': quick_start.get('recommendedStart'),
            'readOrder': quick_start.get('readOrder', [])[:8],
            'highSignalAreas': quick_start.get('highSignalAreas', [])[:8],
        },
        'queryIntent': query_intent,
        'queryProfile': read_profile['name'],
        'retrievalBackend': retrieval_diagnostics.get('backend', 'context-pack'),
        'retrievalDiagnostics': retrieval_diagnostics,
        'rankingDiagnostics': ranking_diagnostics,
        'taskDescription': task_description,
        'availableTasks': available_tasks,
        'contextEngine': {
            'name': 'miloya-csr',
            'enabled': csr_context.get('enabled', False),
            'task': selected_task,
            'route': csr_context.get('route', {}),
            'matchCount': len(csr_context.get('matches', [])),
            'fileCount': len(csr_context.get('files', [])),
        },
        'files': build_read_file_entries(
            file_paths[:read_limits['files']],
            important_files,
            graph,
            representative_snippets,
            index_state,
            snippet_items[:read_limits['snippets']],
        ),
        'snippets': build_read_snippets(
            snippet_items[:read_limits['snippets']],
            representative_snippets,
            query_intent,
        ),
        'flowAnchors': build_read_flow_anchors(file_paths, snippet_items, query_intent, read_limits['anchors']),
        'nextHops': build_read_next_hops(snapshot, file_paths, snippet_items, query_intent)[:read_limits['nextHops']],
        'searchScope': search_scope,
        'hotspots': graph.get('hotspots', [])[:8],
        'moduleDependencies': graph.get('moduleDependencies', [])[:12],
        'externalContext': summarize_external_context(snapshot.get('externalContext', {})),
        'constraints': {
            'preferPayloadFirst': True,
            'avoidRepoWideSearch': True,
            'preserveMainThreadTokens': True,
            'preferLightweightAnswer': True,
            'avoidLongReport': True,
            'preferBriefImplementationSummary': True,
            'primaryGoal': 'locate-code-and-briefly-explain',
            'maxFiles': read_limits['files'],
            'maxSnippets': read_limits['snippets'],
            'maxAnchors': read_limits['anchors'],
            'maxNextHops': read_limits['nextHops'],
            'maxWords': read_limits['maxWords'],
        },
        'recommendedAnswerShape': {
            'style': 'brief-technical-answer',
            'leadWithSummary': True,
            'maxWords': read_limits['maxWords'],
            'sections': ['summary', 'core-files', 'code-anchors', 'brief-flow'],
            'focus': 'tell the model where the code is and briefly how it works',
            'avoid': ['full technical report', 'broad architecture essay', 'repo-wide expansion'],
        },
        'hostHints': {
            'preferredExecution': 'main-thread',
            'consumeAs': 'read-pack',
            'outputStyle': 'lightweight-answer',
            'parentThreadAction': 'answer-from-pack',
            'allowParentThreadExpansion': 'limited',
            'preferredNarrative': 'locate-and-briefly-explain',
            'returnSummaryFirst': True,
        },
    }


def merge_query_intent(query_intent: dict, csr_context: dict) -> dict:
    route = csr_context.get('route', {})
    merged = dict(query_intent)
    labels = list(dict.fromkeys([
        *(query_intent.get('labels', []) or []),
        'csr-routed' if csr_context.get('enabled') else '',
    ]))
    merged['labels'] = [label for label in labels if label]
    if route.get('task'):
        merged['preferredTask'] = route['task']
    merged['routingConfidence'] = route.get('confidence')
    return merged


def enrich_query_intent_with_snapshot(snapshot: dict, query_intent: dict) -> dict:
    merged = dict(query_intent)
    dynamic_hints = build_dynamic_path_hints(snapshot, query_intent)
    if dynamic_hints:
        merged['dynamicPathHints'] = dynamic_hints
    else:
        merged['dynamicPathHints'] = []
    return merged


def build_dynamic_path_hints(snapshot: dict, query_intent: dict) -> list[str]:
    query_terms = set(query_intent.get('keywords', [])) | set(query_intent.get('terms', []))
    if not query_terms:
        return []

    candidates = []
    candidates.extend(snapshot.get('modules', {}).keys())
    candidates.extend(snapshot.get('fileTree', {}).keys())
    candidates.extend(snapshot.get('summary', {}).get('entryPoints', []))
    candidates.extend(snapshot.get('contextHints', {}).get('readOrder', []))
    candidates.extend(item.get('path') for item in snapshot.get('importantFiles', []) if item.get('path'))
    candidates.extend(
        item.get('module')
        for item in snapshot.get('graph', {}).get('pathIndex', [])
        if item.get('module')
    )

    ranked = []
    seen = set()
    for candidate in candidates:
        if not candidate:
            continue
        normalized = normalize_rel_path(candidate)
        if normalized in seen:
            continue
        seen.add(normalized)
        terms = set(extract_text_terms(normalized))
        if not terms:
            continue
        overlap_count = count_fuzzy_term_overlap(terms, query_terms)
        if not overlap_count:
            continue
        # Generic denoise: for multi-term queries, require at least two term hits
        # to avoid broad single-token matches dominating dynamic hints.
        if len(query_terms) >= 3 and overlap_count < 2:
            continue
        score = overlap_count * 12
        basename_terms = set(extract_text_terms(Path(normalized).name))
        score += count_fuzzy_term_overlap(basename_terms, query_terms) * 8
        if normalized.endswith('/'):
            score += 4
        ranked.append((score, normalized))

    ranked.sort(key=lambda item: (-item[0], len(item[1]), item[1]))
    return [path for _, path in ranked[:8]]


def merge_ranked_matches(primary: list[dict], secondary: list[dict]) -> list[dict]:
    merged = []
    seen = set()
    for item in [*primary, *secondary]:
        key = item.get('id') or (
            item.get('path'),
            item.get('startLine'),
            item.get('endLine'),
            item.get('kind'),
        )
        if key in seen:
            continue
        seen.add(key)
        merged.append(item)
    return merged


def query_term_set(query_intent: dict) -> set[str]:
    return set(query_intent.get('keywords', [])) | set(query_intent.get('terms', []))


def compute_match_coverage(item: dict, query_terms: set[str]) -> float:
    if not query_terms:
        return 1.0
    haystack = ' '.join([
        item.get('path') or '',
        item.get('kind') or '',
        item.get('preview') or '',
        ' '.join(item.get('signals', []) or []),
    ])
    haystack_terms = set(extract_text_terms(haystack))
    overlap = count_fuzzy_term_overlap(haystack_terms, query_terms)
    return min(1.0, overlap / max(len(query_terms), 1))


def compute_path_coverage(path: str, query_terms: set[str]) -> float:
    if not query_terms:
        return 1.0
    path_terms = set(extract_text_terms(path))
    overlap = count_fuzzy_term_overlap(path_terms, query_terms)
    return min(1.0, overlap / max(len(query_terms), 1))


def blend_match_sources(
    structural_matches: list[dict],
    lexical_matches: list[dict],
    query_intent: dict,
    lexical_weight: float = 0.8,
    structural_weight: float = 0.2,
) -> list[dict]:
    query_terms = query_term_set(query_intent)
    merged: dict[object, dict] = {}

    def make_key(item: dict) -> object:
        return item.get('id') or (
            item.get('path'),
            item.get('startLine'),
            item.get('endLine'),
            item.get('kind'),
        )

    for item in lexical_matches:
        key = make_key(item)
        merged[key] = {
            'item': dict(item),
            'lexical': float(item.get('score', 0) or 0),
            'structural': 0.0,
        }

    for item in structural_matches:
        key = make_key(item)
        existing = merged.get(key)
        if existing is None:
            merged[key] = {
                'item': dict(item),
                'lexical': 0.0,
                'structural': float(item.get('score', 0) or 0),
            }
            continue
        existing['structural'] = max(existing['structural'], float(item.get('score', 0) or 0))
        if existing['lexical'] <= 0:
            existing['item'] = dict(item)

    ranked = []
    for payload in merged.values():
        item = payload['item']
        coverage = compute_match_coverage(item, query_terms)
        blended = (
            lexical_weight * payload['lexical']
            + structural_weight * payload['structural']
            + coverage * 24.0
        )
        if payload['lexical'] <= 0 and payload['structural'] > 0:
            blended -= 72.0 + max(0.0, (0.6 - coverage) * 80.0)
        enriched = dict(item)
        enriched['score'] = blended
        enriched['coverage'] = round(coverage, 3)
        enriched['lexicalScore'] = round(payload['lexical'], 3)
        enriched['structuralScore'] = round(payload['structural'], 3)
        ranked.append(enriched)

    ranked.sort(key=lambda item: (-float(item.get('score', 0) or 0), item.get('path') or '', item.get('startLine') or 0))
    return ranked


def prioritize_matches_by_coverage(matches: list[dict], query_intent: dict, min_coverage: float = 0.2) -> list[dict]:
    query_terms = query_term_set(query_intent)
    if len(query_terms) < 2:
        return matches
    high = []
    low = []
    for item in matches:
        coverage = compute_match_coverage(item, query_terms)
        enriched = dict(item)
        enriched['coverage'] = round(coverage, 3)
        lexical_score = float(enriched.get('lexicalScore', 0) or 0)
        structural_score = float(enriched.get('structuralScore', 0) or 0)
        structural_only = structural_score > 0 and lexical_score <= 0
        if coverage >= min_coverage and not structural_only:
            high.append(enriched)
        else:
            if structural_only and len(query_terms) >= 2:
                enriched['score'] = float(enriched.get('score', 0) or 0) - 48.0
            low.append(enriched)
    low.sort(
        key=lambda item: (
            -float(item.get('coverage', 0) or 0),
            -float(item.get('score', 0) or 0),
            item.get('path') or '',
            item.get('startLine') or 0,
        ),
    )
    return high + low


def prioritize_files_by_coverage(
    file_paths: list[str],
    snippet_items: list[dict],
    query_intent: dict,
    min_coverage: float = 0.2,
) -> list[str]:
    query_terms = query_term_set(query_intent)
    if len(query_terms) < 2:
        return file_paths

    snippet_cov_by_path: dict[str, float] = {}
    for item in snippet_items:
        path = item.get('path')
        if not path:
            continue
        cov = compute_match_coverage(item, query_terms)
        if cov > snippet_cov_by_path.get(path, -1.0):
            snippet_cov_by_path[path] = cov

    high: list[str] = []
    low: list[tuple[float, str]] = []
    for path in file_paths:
        coverage = max(compute_path_coverage(path, query_terms), snippet_cov_by_path.get(path, 0.0))
        if coverage >= min_coverage:
            high.append(path)
        else:
            low.append((coverage, path))
    low.sort(key=lambda item: (-item[0], len(item[1]), item[1]))
    return high + [path for _, path in low]


def build_ranking_diagnostics(
    snippet_items: list[dict],
    file_paths: list[str],
    query_intent: dict,
    csr_context: dict,
    topk_snippets: int,
    topk_files: int,
) -> dict:
    query_terms = query_term_set(query_intent)
    snippet_top = snippet_items[:max(topk_snippets, 1)]
    file_top = file_paths[:max(topk_files, 1)]

    snippet_cov_values = [compute_match_coverage(item, query_terms) for item in snippet_top] or [0.0]
    file_cov_values = [compute_path_coverage(path, query_terms) for path in file_top] or [0.0]

    csr_keys = {
        item.get('id') or (item.get('path'), item.get('startLine'), item.get('endLine'), item.get('kind'))
        for item in csr_context.get('matches', [])
    }
    top_keys = {
        item.get('id') or (item.get('path'), item.get('startLine'), item.get('endLine'), item.get('kind'))
        for item in snippet_top
    }
    csr_ratio = 0.0 if not top_keys else len(top_keys & csr_keys) / len(top_keys)
    structural_only = 0
    for item in snippet_top:
        lexical_score = float(item.get('lexicalScore', 0) or 0)
        structural_score = float(item.get('structuralScore', 0) or 0)
        if structural_score > 0 and lexical_score <= 0:
            structural_only += 1
    structural_only_ratio = 0.0 if not snippet_top else structural_only / len(snippet_top)

    return {
        'topkCoverageAvg': round(sum(snippet_cov_values) / len(snippet_cov_values), 3),
        'top1Coverage': round(snippet_cov_values[0], 3),
        'topkFileCoverageAvg': round(sum(file_cov_values) / len(file_cov_values), 3),
        'csrContributionRatio': round(csr_ratio, 3),
        'csrStructuralOnlyRatio': round(structural_only_ratio, 3),
    }


def merge_ordered_paths(primary: list[str], secondary: list[str]) -> list[str]:
    merged = []
    seen = set()
    for path in [*primary, *secondary]:
        normalized = normalize_rel_path(path) if path else ''
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        merged.append(normalized)
    return merged


def collect_hint_file_paths(
    index_state: dict | None,
    query_intent: dict,
    read_profile: dict,
    limit: int = 12,
) -> list[str]:
    index_files = (index_state or {}).get('files', {})
    hints = query_intent.get('dynamicPathHints', [])[:6]
    if not index_files or not hints:
        return []

    query_terms = set(query_intent.get('keywords', []))
    exact_terms = set(query_intent.get('terms', []))
    test_query = is_test_query(query_intent)
    ranked = []

    for path in index_files:
        normalized = normalize_rel_path(path)
        lowered = normalized.lower()
        best_hint_score = 0

        for index, hint in enumerate(hints):
            normalized_hint = normalize_rel_path(hint).lower()
            if lowered == normalized_hint or lowered.startswith(normalized_hint.rstrip('/') + '/'):
                best_hint_score = max(best_hint_score, 36 - index * 4)
            elif normalized_hint and normalized_hint in lowered:
                best_hint_score = max(best_hint_score, 18 - index * 2)

        if best_hint_score <= 0:
            continue

        path_terms = set(extract_text_terms(normalized))
        role = infer_read_file_role(normalized, {}) or ''
        score = best_hint_score
        score += min(count_fuzzy_term_overlap(path_terms, query_terms), 4) * 8
        score += min(count_fuzzy_term_overlap(path_terms, exact_terms), 3) * 10
        if role_matches_profile(role, read_profile):
            score += 10
        if is_documentation_file(normalized) and not is_documentation_query(query_intent):
            score -= 18
        if is_script_like_file(normalized) and not is_script_query(query_intent):
            score -= 10
        if is_probably_test_path(normalized) and not test_query:
            score -= 70
        fuzzy_exact_overlap = count_fuzzy_term_overlap(path_terms, exact_terms)
        score += exact_coverage_penalty(fuzzy_exact_overlap, exact_terms, role, read_profile)

        ranked.append((score, normalized))

    ranked.sort(key=lambda item: (-item[0], len(item[1]), item[1]))
    return [path for _, path in ranked[:limit]]


def merge_search_scope(base_scope: dict, csr_context: dict) -> dict:
    merged_paths = merge_ordered_paths(
        (csr_context.get('searchScope') or {}).get('preferPaths', []),
        base_scope.get('preferPaths', []),
    )
    notes = []
    for note in [*((csr_context.get('searchScope') or {}).get('notes', [])), *base_scope.get('notes', [])]:
        if note and note not in notes:
            notes.append(note)
    return {
        **base_scope,
        'preferPaths': merged_paths[:10],
        'notes': notes[:5],
    }


def build_report_payload(
    snapshot: dict,
    index_state: dict | None,
    task: str,
    query: str | None,
    sqlite_db_path: str | None = None,
) -> dict:
    read_payload = build_read_payload(
        snapshot,
        index_state,
        task,
        query,
        sqlite_db_path=sqlite_db_path,
    )
    query_intent = read_payload.get('queryIntent', {})
    report_limits = determine_report_limits(query_intent)
    graph = snapshot.get('graph', {})
    summary = snapshot.get('summary', {})

    core_files = read_payload.get('files', [])[:report_limits['coreFiles']]
    snippets = read_payload.get('snippets', [])[:report_limits['snippets']]
    flow_anchors = read_payload.get('flowAnchors', [])[:report_limits['anchors']]
    next_hops = read_payload.get('nextHops', [])[:report_limits['nextHops']]
    search_scope = read_payload.get('searchScope', {})
    prefer_paths = search_scope.get('preferPaths', [])
    focus_modules = infer_focus_modules(prefer_paths)

    return {
        'mode': 'report',
        'reportMode': 'deep-pack',
        'reportPackVersion': '1.0',
        'task': read_payload.get('task'),
        'query': read_payload.get('query'),
        'snapshotPath': read_payload.get('snapshotPath'),
        'sourceFingerprint': read_payload.get('sourceFingerprint'),
        'freshness': read_payload.get('freshness'),
        'analysis': read_payload.get('analysis'),
        'questionType': {
            'labels': query_intent.get('labels', []),
            'keywords': query_intent.get('keywords', [])[:16],
            'confidence': infer_report_confidence(query_intent, core_files, snippets),
        },
        'summary': {
            'project': summary.get('name'),
            'type': summary.get('type'),
            'description': summary.get('description'),
            'techStack': summary.get('techStack', [])[:8],
            'architecture': snapshot.get('architecture'),
            'entryPoints': summary.get('entryPoints', [])[:8],
        },
        'taskDescription': read_payload.get('taskDescription'),
        'coreFiles': core_files,
        'snippets': snippets,
        'flowAnchors': flow_anchors,
        'nextHops': next_hops,
        'focusModules': focus_modules,
        'moduleDependencies': filter_report_module_dependencies(
            graph.get('moduleDependencies', []),
            focus_modules,
            report_limits['moduleDependencies'],
        ),
        'hotspots': graph.get('hotspots', [])[:report_limits['hotspots']],
        'searchScope': search_scope,
        'constraints': {
            'preferSubagent': True,
            'fallbackToMainThread': True,
            'preferEvidence': True,
            'avoidRepoWideSearch': True,
            'preserveMainThreadTokens': True,
            'delegationRequiredIfAvailable': True,
            'allowParentThreadExpansion': False,
            'parentThreadAction': 'stop-after-pack',
            'maxFiles': report_limits['coreFiles'],
            'maxSnippets': report_limits['snippets'],
            'maxAnchors': report_limits['anchors'],
            'maxNextHops': report_limits['nextHops'],
            'maxWords': report_limits['maxWords'],
        },
        'recommendedReportShape': {
            'style': 'deep-technical-report',
            'leadWithSummary': True,
            'maxWords': report_limits['maxWords'],
            'sections': determine_report_sections(query_intent, read_payload.get('task')),
            'evidenceStyle': 'cite file paths, line anchors, and clearly separate facts from inference',
        },
        'hostHints': {
            'preferredExecution': 'subagent',
            'fallbackExecution': 'main-thread',
            'consumeAs': 'deep-pack',
            'outputStyle': 'pack-only',
            'parentThreadAction': 'stop-after-pack',
            'delegationRequiredIfAvailable': True,
            'allowParentThreadExpansion': False,
            'returnSummaryFirst': True,
        },
        'externalContext': read_payload.get('externalContext'),
        'availableTasks': read_payload.get('availableTasks', []),
    }


def describe_task(snapshot: dict, task: str) -> str | None:
    task_pack = snapshot.get('contextPacks', {}).get(task, {})
    if task_pack.get('description'):
        return task_pack['description']

    for sample in snapshot.get('retrieval', {}).get('sampleQueries', []):
        if task.replace('-', ' ') in sample:
            return sample
    return None


def build_default_read_paths(snapshot: dict, task_pack: dict) -> list[str]:
    ordered_paths = []
    ordered_paths.extend(snapshot.get('contextHints', {}).get('readOrder', [])[:6])
    ordered_paths.extend(snapshot.get('summary', {}).get('entryPoints', [])[:6])
    ordered_paths.extend(task_pack.get('files', [])[:8])

    deduped = []
    seen = set()
    for path in ordered_paths:
        if not path or path in seen:
            continue
        seen.add(path)
        deduped.append(path)
        if len(deduped) >= 8:
            break
    return deduped


def normalize_query_text(query: str | None) -> str | None:
    if not query:
        return query

    normalized = query.replace('\ufffd', ' ')
    normalized = re.sub(r'[^A-Za-z0-9_\s\-/.:#@\u4e00-\u9fff]+', ' ', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized or query


def extract_text_terms(text: str | None) -> list[str]:
    if not text:
        return []

    normalized = normalize_query_text(text) or ''
    normalized = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', normalized)
    normalized = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', normalized)
    tokens = re.findall(r'[A-Za-z][A-Za-z0-9]*|[\u4e00-\u9fff]+|\d+', normalized.lower())

    deduped: list[str] = []
    seen = set()
    for token in tokens:
        token = token.strip()
        if len(token) < 2 or token in seen:
            continue
        seen.add(token)
        deduped.append(token)
    return deduped


def extract_query_terms(query: str | None) -> list[str]:
    raw_terms = extract_text_terms(query)
    collected: list[str] = []
    seen = set()
    for term in raw_terms:
        token = term.strip()
        if len(token) < 2 or token in seen:
            continue
        seen.add(token)
        collected.append(token)
    return collected[:24]


def is_probably_test_path(path: str) -> bool:
    lowered = normalize_rel_path(path).lower()
    file_name = Path(lowered).name
    file_terms = set(extract_text_terms(lowered))
    return (
        '.test.' in lowered
        or '.spec.' in lowered
        or '_test.' in lowered
        or '.e2e.' in lowered
        or file_name.startswith(('test_', 'spec_'))
        or bool(file_terms & {'test', 'tests', 'spec', 'fixture', 'fixtures', 'e2e', 'harness'})
    )


def expand_query_terms(terms: list[str]) -> list[str]:
    return list(dict.fromkeys(terms))[:32]


def determine_read_limits(query_intent: dict) -> dict[str, int]:
    return {
        'files': 4,
        'snippets': 3,
        'nextHops': 2,
        'anchors': 4,
        'maxWords': 380,
    }


def select_read_profile(query_intent: dict) -> dict:
    labels = set(query_intent.get('labels', []))
    if 'test-surface' in labels or 'tests' in labels:
        return {
            'name': 'tests',
            'focusTerms': set(),
            'suppressTerms': set(),
            'focusEntrySuffixes': {'test.ts', 'test.py', 'test.js', 'spec.ts', 'spec.js'},
            'targetRoles': {'Test surface'},
            'boostSymbolTerms': set(),
            'penalizeSymbolTerms': set(),
        }
    if 'configuration' in labels or 'config' in labels:
        return {
            'name': 'config',
            'focusTerms': set(),
            'suppressTerms': set(),
            'focusEntrySuffixes': {'config.ts', 'config.py', 'settings.ts', 'settings.py'},
            'targetRoles': {'Configuration', 'Type definition'},
            'boostSymbolTerms': set(),
            'penalizeSymbolTerms': set(),
        }
    if 'execution-path' in labels or 'failure-trace' in labels or 'trace' in labels:
        return {
            'name': 'trace',
            'focusTerms': set(),
            'suppressTerms': set(),
            'focusEntrySuffixes': {'main.ts', 'index.ts', 'app.ts', 'app.py'},
            'targetRoles': {'Routing / transport', 'Handler / controller', 'Service', 'Runtime / integration'},
            'boostSymbolTerms': set(),
            'penalizeSymbolTerms': set(),
        }
    if 'feature' in labels or 'implementation-surface' in labels:
        return {
            'name': 'feature',
            'focusTerms': set(),
            'suppressTerms': set(),
            'focusEntrySuffixes': {'main.ts', 'index.ts', 'app.tsx', 'app.py'},
            'targetRoles': {'Service', 'Handler / controller', 'Runtime / integration', 'UI component'},
            'boostSymbolTerms': set(),
            'penalizeSymbolTerms': set(),
        }
    return {
        'name': 'generic',
        'focusTerms': set(),
        'suppressTerms': set(),
        'focusEntrySuffixes': set(),
        'targetRoles': set(),
        'boostSymbolTerms': set(),
        'penalizeSymbolTerms': set(),
    }


def determine_report_limits(query_intent: dict) -> dict[str, int]:
    read_limits = determine_read_limits(query_intent)
    return {
        'coreFiles': max(read_limits['files'], 6),
        'snippets': max(read_limits['snippets'], 6),
        'anchors': max(read_limits['anchors'], 6),
        'nextHops': max(read_limits['nextHops'], 4),
        'moduleDependencies': 10,
        'hotspots': 8,
        'maxWords': 1400,
    }


def infer_focus_modules(file_paths: list[str]) -> list[str]:
    modules = []
    seen = set()
    for path in file_paths:
        module = infer_path_module(path)
        if not module or module in seen:
            continue
        seen.add(module)
        modules.append(module)
        if len(modules) >= 6:
            break
    return modules


def infer_path_module(path: str) -> str:
    normalized = normalize_rel_path(path)
    parts = Path(normalized).parts
    if not parts:
        return './'
    directory_parts = list(parts[:-1]) if Path(normalized).suffix else list(parts)
    if not directory_parts:
        return './'
    depth = 2 if len(directory_parts) >= 2 else 1
    return '/'.join(directory_parts[:depth]) + '/'


def filter_report_module_dependencies(
    dependencies: list[dict],
    focus_modules: list[str],
    limit: int,
) -> list[dict]:
    if not dependencies:
        return []
    focus_set = set(focus_modules)
    prioritized = []
    deferred = []
    for item in dependencies:
        source = item.get('source')
        target = item.get('target')
        if source in focus_set or target in focus_set:
            prioritized.append(item)
        else:
            deferred.append(item)
    return (prioritized + deferred)[:limit]


def infer_report_confidence(query_intent: dict, core_files: list[dict], snippets: list[dict]) -> float:
    labels = query_intent.get('labels', [])
    evidence_count = len(core_files) + len(snippets)
    if not evidence_count:
        return 0.35
    confidence = 0.45 + min(len(labels), 3) * 0.1 + min(evidence_count, 8) * 0.03
    return round(min(confidence, 0.95), 2)


def determine_report_sections(query_intent: dict, task: str | None) -> list[str]:
    sections = ['summary', 'core-files', 'code-anchors']

    if task in {'bugfix-investigation', 'code-review'}:
        sections.append('risks')

    sections.append('facts-vs-inference')

    seen = set()
    ordered = []
    for section in sections:
        if section in seen:
            continue
        seen.add(section)
        ordered.append(section)
    return ordered


def prioritize_read_file_paths(
    file_paths: list[str],
    snippet_items: list[dict],
    query_intent: dict,
    read_profile: dict,
) -> list[str]:
    query_terms = set(query_intent.get('keywords', []))
    exact_terms = set(query_intent.get('terms', []))
    test_query = is_test_query(query_intent)
    snippet_paths = [item.get('path') for item in snippet_items if item.get('path')]
    ordered_candidates = []
    ordered_candidates.extend(snippet_paths)
    ordered_candidates.extend(file_paths)

    deduped = []
    seen = set()
    for path in ordered_candidates:
        if not path or path in seen:
            continue
        seen.add(path)
        deduped.append(path)

    def score_path(path: str) -> tuple[int, int, str]:
        lowered = path.lower()
        path_terms = set(extract_text_terms(path))
        role = infer_read_file_role(path, {}) or ''
        score = 0

        if path in snippet_paths:
            score += 40

        if role_matches_profile(role, read_profile):
            score += 14
        if is_documentation_file(path) and not is_documentation_query(query_intent):
            score -= 52
        if is_script_like_file(path) and not is_script_query(query_intent):
            score -= 14
        if is_probably_test_path(path) and not test_query:
            score -= 84

        keyword_overlap = len(path_terms & query_terms)
        if keyword_overlap:
            score += min(keyword_overlap, 3) * 12
        exact_overlap = len(path_terms & exact_terms)
        if exact_overlap:
            score += min(exact_overlap, 2) * 18
        focus_overlap = count_fuzzy_term_overlap(path_terms, read_profile.get('focusTerms', set()))
        if focus_overlap:
            score += min(focus_overlap, 3) * 8
        suppress_overlap = count_fuzzy_term_overlap(path_terms, read_profile.get('suppressTerms', set()))
        if suppress_overlap:
            score -= min(suppress_overlap, 2) * 6
        fuzzy_exact_overlap = count_fuzzy_term_overlap(path_terms, exact_terms)
        score += exact_coverage_penalty(fuzzy_exact_overlap, exact_terms, role, read_profile)
        if path_terms & {'constant', 'constants', 'i18n', 'locale', 'locales', 'asset', 'assets'}:
            score -= 8

        score += score_path_with_profile(path, query_intent, read_profile)

        return (-score, 0 if path in snippet_paths else 1, path)

    return sorted(deduped, key=score_path)


def score_path_with_profile(path: str, query_intent: dict, read_profile: dict) -> int:
    score = 0
    lowered = path.lower()
    path_terms = set(extract_text_terms(lowered))
    query_terms = set(query_intent.get('keywords', []))
    exact_terms = set(query_intent.get('terms', []))
    role = infer_read_file_role(path, {}) or ''
    test_query = is_test_query(query_intent)

    focus_overlap = count_fuzzy_term_overlap(path_terms, read_profile.get('focusTerms', set()))
    if focus_overlap:
        score += min(focus_overlap, 3) * 8
    suppress_overlap = count_fuzzy_term_overlap(path_terms, read_profile.get('suppressTerms', set()))
    if suppress_overlap:
        score -= min(suppress_overlap, 2) * 6
    if any(lowered.endswith(suffix) for suffix in read_profile.get('focusEntrySuffixes', set())):
        score += 12
    if role_matches_profile(role, read_profile):
        score += 10
    if query_terms and path_terms & query_terms:
        score += min(len(path_terms & query_terms), 4) * 8
    if exact_terms and path_terms & exact_terms:
        score += min(len(path_terms & exact_terms), 3) * 10
    fuzzy_exact_overlap = count_fuzzy_term_overlap(path_terms, exact_terms)
    score += exact_coverage_penalty(fuzzy_exact_overlap, exact_terms, role, read_profile)
    if is_documentation_file(path) and not is_documentation_query(query_intent):
        score -= 16
    if is_script_like_file(path) and not is_script_query(query_intent):
        score -= 8
    if is_probably_test_path(path) and not test_query:
        score -= 42

    for index, hint in enumerate(query_intent.get('dynamicPathHints', [])[:6]):
        normalized_hint = normalize_rel_path(hint).lower()
        if lowered == normalized_hint or lowered.startswith(normalized_hint.rstrip('/') + '/'):
            score += max(16 - index * 2, 6)
        elif normalized_hint and normalized_hint in lowered:
            score += max(10 - index, 3)

    return score


def is_suppressed_by_profile(path: str, query_intent: dict, read_profile: dict) -> bool:
    return False


def refine_read_file_paths(snapshot: dict, file_paths: list[str], query_intent: dict, read_profile: dict) -> list[str]:
    deduped = []
    seen = set()
    for path in file_paths:
        normalized = normalize_rel_path(path)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)

    if query_intent.get('dynamicPathHints'):
        return deduped

    entry_points = []
    seen_entries = set()
    for path in snapshot.get('summary', {}).get('entryPoints', []):
        normalized = normalize_rel_path(path)
        if normalized in seen and normalized not in seen_entries:
            entry_points.append(normalized)
            seen_entries.add(normalized)

    remainder = [path for path in deduped if path not in seen_entries]
    return entry_points + remainder


def infer_query_intent_framework(query: str | None) -> dict:
    if not query:
        return {
            'labels': ['general-read'],
            'keywords': [],
            'terms': [],
            'preferredTask': 'understand-project',
        }

    terms = extract_query_terms(query)
    keywords = expand_query_terms(terms)
    
    query_lower = query.lower()
    labels = ['general-read']
    preferred_task = 'understand-project'

    if 'bug' in query_lower or '失败' in query_lower or '排查' in query_lower or '修复' in query_lower:
        preferred_task = 'bugfix-investigation'
        labels.append('trace')
    elif 'add' in query_lower or '新增' in query_lower or '支持' in query_lower or 'feature' in query_lower:
        preferred_task = 'feature-delivery'
        labels.append('feature')
    elif 'review' in query_lower or 'review' in query_lower or '代码审查' in query_lower:
        preferred_task = 'code-review'
    elif 'config' in query_lower or '配置' in query_lower or 'workflow' in query_lower:
        labels.append('config')

    if 'workflow' in query_lower or 'release' in query_lower:
        labels.append('config')

    return {
        'labels': labels,
        'keywords': keywords[:20],
        'terms': terms[:20],
        'preferredTask': preferred_task,
    }


infer_query_intent = infer_query_intent_framework
infer_query_intent_v2 = infer_query_intent_framework


def rerank_read_matches(matches: list[dict], query_intent: dict, read_profile: dict | None = None) -> list[dict]:
    read_profile = read_profile or select_read_profile(query_intent)
    query_terms = set(query_intent.get('keywords', []))
    exact_terms = set(query_intent.get('terms', []))
    test_query = is_test_query(query_intent)
    reranked = []

    for item in matches:
        bonus = 0
        path = (item.get('path') or '').lower()
        kind = (item.get('kind') or '').lower()
        preview = (item.get('preview') or '').lower()
        preview_head = preview.splitlines()[0] if preview else ''
        signals = ' '.join(item.get('signals', [])).lower()
        haystack = ' '.join([path, kind, preview, signals])
        haystack_terms = set(extract_text_terms(haystack))
        symbol_terms = set(extract_text_terms(preview_head))
        role = infer_read_file_role(path, item) or ''

        if role_matches_profile(role, read_profile):
            bonus += 12
        if is_documentation_file(path) and not is_documentation_query(query_intent):
            bonus -= 58
        if kind == 'link' and (
            'feature' in query_intent.get('labels', [])
            or 'trace' in query_intent.get('labels', [])
        ) and not is_documentation_query(query_intent):
            bonus -= 36
        if is_script_like_file(path) and not is_script_query(query_intent):
            bonus -= 14
        if is_probably_test_path(path) and not test_query:
            bonus -= 90
        suffix = Path(path).suffix.lower()
        if suffix and suffix not in CODE_LIKE_EXTENSIONS and not is_documentation_file(path):
            bonus -= 28

        keyword_overlap = len(haystack_terms & query_terms)
        if keyword_overlap:
            bonus += min(keyword_overlap, 4) * 6
        exact_overlap = len(haystack_terms & exact_terms)
        if exact_overlap:
            bonus += min(exact_overlap, 3) * 12
        fuzzy_exact_overlap = count_fuzzy_term_overlap(haystack_terms, exact_terms)
        bonus += exact_coverage_penalty(fuzzy_exact_overlap, exact_terms, role, read_profile)
        exact_symbol_overlap = len(symbol_terms & exact_terms)
        if exact_symbol_overlap:
            bonus += min(exact_symbol_overlap, 2) * 18
        if exact_terms and fuzzy_exact_overlap == 0 and keyword_overlap == 0:
            bonus -= 64
        elif exact_terms and fuzzy_exact_overlap == 0:
            bonus -= 24

        bonus += score_match_with_profile(path, symbol_terms, query_intent, read_profile)

        reranked.append((item.get('score', 0) + bonus, item))

    reranked.sort(key=lambda pair: (-pair[0], pair[1].get('path') or '', pair[1].get('startLine') or 0))
    return [item for _, item in reranked]


def score_match_with_profile(path: str, symbol_terms: set[str], query_intent: dict, read_profile: dict) -> int:
    score = 0
    lowered = path.lower()
    query_terms = set(query_intent.get('keywords', []))
    exact_terms = set(query_intent.get('terms', []))
    path_terms = set(extract_text_terms(lowered))
    role = infer_read_file_role(path, {}) or ''
    test_query = is_test_query(query_intent)

    focus_overlap = count_fuzzy_term_overlap(path_terms, read_profile.get('focusTerms', set()))
    if focus_overlap:
        score += min(focus_overlap, 3) * 8
    suppress_overlap = count_fuzzy_term_overlap(path_terms, read_profile.get('suppressTerms', set()))
    if suppress_overlap:
        score -= min(suppress_overlap, 2) * 6
    if any(lowered.endswith(suffix) for suffix in read_profile.get('focusEntrySuffixes', set())):
        score += 14
    if role_matches_profile(role, read_profile):
        score += 10

    boosted = symbol_terms & read_profile.get('boostSymbolTerms', set())
    if boosted:
        score += min(len(boosted), 3) * 8
    penalized = symbol_terms & read_profile.get('penalizeSymbolTerms', set())
    if penalized:
        score -= min(len(penalized), 2) * 6
    if query_terms and symbol_terms & query_terms:
        score += min(len(symbol_terms & query_terms), 2) * 6
    fuzzy_keyword_overlap = count_fuzzy_term_overlap(path_terms, query_terms)
    if fuzzy_keyword_overlap:
        score += min(fuzzy_keyword_overlap, 4) * 8
    fuzzy_exact_overlap = count_fuzzy_term_overlap(path_terms, exact_terms)
    if fuzzy_exact_overlap:
        score += min(fuzzy_exact_overlap, 3) * 10
    score += exact_coverage_penalty(fuzzy_exact_overlap, exact_terms, role, read_profile)

    for index, hint in enumerate(query_intent.get('dynamicPathHints', [])[:6]):
        normalized_hint = normalize_rel_path(hint).lower()
        if lowered == normalized_hint or lowered.startswith(normalized_hint.rstrip('/') + '/'):
            score += max(14 - index * 2, 6)
        elif normalized_hint and normalized_hint in lowered:
            score += max(8 - index, 3)

    if lowered.endswith('.json') and not (path_terms & (query_terms | exact_terms)):
        score -= 10
    if is_documentation_file(path) and not is_documentation_query(query_intent):
        score -= 24
    if is_script_like_file(path) and not is_script_query(query_intent):
        score -= 6
    if is_probably_test_path(path) and not test_query:
        score -= 36

    return score


def role_matches_profile(role: str | None, read_profile: dict) -> bool:
    return bool(role and role in read_profile.get('targetRoles', set()))


def exact_coverage_penalty(
    fuzzy_exact_overlap: int,
    exact_terms: set[str],
    role: str | None,
    read_profile: dict,
) -> int:
    if not exact_terms or role_matches_profile(role, read_profile):
        return 0
    if len(exact_terms) >= 3 and fuzzy_exact_overlap <= 1:
        return -26
    if len(exact_terms) >= 2 and fuzzy_exact_overlap == 0:
        return -16
    return 0


def is_documentation_query(query_intent: dict) -> bool:
    labels = set(query_intent.get('labels', []))
    return 'documentation' in labels


def is_documentation_file(path: str) -> bool:
    normalized = normalize_rel_path(path).lower()
    name = Path(normalized).name.lower()
    suffix = Path(normalized).suffix.lower()
    file_terms = set(extract_text_terms(name))
    return (
        suffix in {'.md', '.mdx', '.rst', '.txt', '.adoc'}
        or name in {'readme', 'readme.md', 'changelog.md', 'contributing.md', 'license', 'license.md', 'security.md'}
        or bool(file_terms & {'readme', 'changelog', 'guide', 'manual', 'wiki', 'documentation', 'doc'})
    )


def is_script_query(query_intent: dict) -> bool:
    labels = set(query_intent.get('labels', []))
    return 'script' in labels


def is_test_query(query_intent: dict) -> bool:
    labels = set(query_intent.get('labels', []))
    return 'tests' in labels or 'test-surface' in labels


def is_script_like_file(path: str) -> bool:
    normalized = normalize_rel_path(path).lower()
    suffix = Path(normalized).suffix.lower()
    name_terms = set(extract_text_terms(Path(normalized).name))
    return suffix in {'.sh', '.ps1', '.bat', '.cmd'} or bool(name_terms & {'script', 'setup', 'build', 'release', 'deploy', 'cli'})


def count_fuzzy_term_overlap(left: set[str], right: set[str]) -> int:
    matched = 0
    for token in left:
        token_variants = build_term_variants(token)
        for other in right:
            other_variants = build_term_variants(other)
            if token_variants & other_variants:
                matched += 1
                break
    return matched


def should_keep_related_expansion(base_term: str, related_term: str) -> bool:
    base = (base_term or '').strip().lower()
    related = (related_term or '').strip().lower()
    if not base or not related or related == base:
        return False
    if len(related) < 3 or related in NOISY_QUERY_EXPANSION_TERMS:
        return False

    base_variants = build_term_variants(base)
    related_variants = build_term_variants(related)
    if base_variants & related_variants:
        return True

    if len(base) >= 4 and (base in related or related in base):
        return True

    return False


def build_term_variants(token: str) -> set[str]:
    normalized = (token or '').strip().lower()
    if not normalized:
        return set()

    variants = {normalized}
    if len(normalized) >= 4:
        if normalized.endswith('ies'):
            variants.add(normalized[:-3] + 'y')
        if normalized.endswith('es'):
            variants.add(normalized[:-2])
        if normalized.endswith('s'):
            variants.add(normalized[:-1])
        else:
            variants.add(normalized + 's')
    return {item for item in variants if item}


def resolve_read_task(
    requested_task: str,
    available_tasks: list[str],
    retrieval: dict,
    query_intent: dict,
) -> str:
    default_task = retrieval.get('defaultTask', 'understand-project')
    if requested_task in available_tasks and requested_task != default_task:
        return requested_task

    preferred_task = query_intent.get('preferredTask')
    if preferred_task in available_tasks:
        return preferred_task

    if requested_task in available_tasks:
        return requested_task

    return default_task


def build_read_file_entries(
    file_paths: list[str],
    important_files: list[dict],
    graph: dict,
    representative_snippets: list[dict],
    index_state: dict | None,
    snippet_items: list[dict],
) -> list[dict]:
    important_by_path = {item['path']: item for item in important_files}
    hotspot_by_path = {item['path']: item for item in graph.get('hotspots', [])}
    index_files = (index_state or {}).get('files', {})
    snippet_by_path = {}
    for item in snippet_items:
        if item.get('path') and item.get('preview'):
            snippet_by_path.setdefault(item['path'], item)
    for item in representative_snippets:
        snippet_by_path.setdefault(item['path'], item)

    entries = []
    for path in file_paths:
        important = important_by_path.get(path, {})
        hotspot = hotspot_by_path.get(path, {})
        indexed = index_files.get(path, {})
        snippet = snippet_by_path.get(path, {})
        inferred_role = infer_read_file_role(path, snippet)
        role = important.get('role')
        if not role or role in {'Implementation', 'Data model'}:
            role = inferred_role or role
        language = important.get('language') or indexed.get('language')
        lines = important.get('lines') or indexed.get('lineCount')
        why_important = important.get('whyImportant') or infer_read_file_reason(path, snippet, hotspot, indexed)
        entries.append({
            'path': path,
            'role': role,
            'language': language,
            'lines': lines,
            'whyImportant': why_important,
            'score': important.get('score'),
            'hotspot': {
                'inbound': hotspot.get('inbound', 0),
                'outbound': hotspot.get('outbound', 0),
                'signals': hotspot.get('signals', 0),
            },
            'previewReason': snippet.get('reason'),
        })
    return entries


def infer_read_file_role(path: str, snippet: dict) -> str | None:
    lowered = path.lower()
    snippet_kind = (snippet.get('kind') or '').lower()
    file_name = Path(lowered).name.lower()
    file_terms = set(extract_text_terms(file_name))
    path_terms = set(extract_text_terms(lowered))

    if lowered.endswith(('main.ts', 'app.tsx', 'preload.ts', 'index.html')):
        return 'Entry point'
    if lowered.endswith(('.tsx', '.jsx')) or file_terms & {'component', 'view', 'screen', 'page'}:
        return 'UI component'
    if lowered.endswith('.d.ts') or file_terms & {'type', 'types'} or path_terms & {'schema', 'model', 'interface'}:
        return 'Type definition'
    if is_documentation_file(path):
        return 'Documentation'
    if Path(lowered).suffix in {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf'}:
        return 'Configuration'
    if path_terms & {'config', 'setting', 'settings', 'env', 'option', 'workflow', 'pipeline', 'release'}:
        return 'Configuration'
    if path_terms & {'manager', 'runtime', 'adapter', 'gateway', 'connector', 'agentengine', 'plugin'}:
        return 'Runtime / integration'
    if path_terms & {'route', 'router', 'dispatch', 'delivery', 'transport'}:
        return 'Routing / transport'
    if path_terms & {'handler', 'controller', 'middleware'}:
        return 'Handler / controller'
    if path_terms & {'store', 'sqlite', 'storage', 'repository'}:
        return 'Store'
    if 'service' in file_terms or 'service' in path_terms:
        return 'Service'
    if is_probably_test_path(path):
        return 'Test surface'
    if snippet_kind == 'link':
        return 'Documentation / link source'
    return None


def infer_read_file_reason(path: str, snippet: dict, hotspot: dict, indexed: dict) -> str | None:
    reasons = []
    line_count = indexed.get('lineCount')
    lowered = path.lower()
    snippet_kind = (snippet.get('kind') or '').lower()
    snippet_reason = snippet.get('reason')
    snippet_signals = snippet.get('signals', [])
    inbound = hotspot.get('inbound', 0)
    outbound = hotspot.get('outbound', 0)
    signals = hotspot.get('signals', 0)

    if line_count:
        reasons.append(f'{line_count} lines')
    if snippet_reason:
        reasons.append(str(snippet_reason))
    elif snippet_kind == 'link':
        reasons.append('contains guide or external link definitions')
    elif snippet_kind == 'action-flow':
        reasons.append('contains action-oriented implementation flow')
    elif snippet_kind == 'config-flow':
        reasons.append('contains configuration persistence flow')
    elif snippet_kind == 'config-type':
        reasons.append('contains configuration-related type definitions')
    elif snippet_kind == 'function':
        reasons.append('contains implementation anchors')

    if snippet_signals:
        reasons.append('signals: ' + ', '.join(snippet_signals[:3]))

    if inbound or outbound:
        reasons.append(f'hotspot in={inbound} out={outbound}')
    elif signals:
        reasons.append(f'{signals} structural signals')

    if set(extract_text_terms(lowered)) & {'skillmanager', 'runtime', 'adapter', 'gateway'}:
        reasons.append('participates in runtime or skill execution flow')
    else:
        inferred_role = infer_read_file_role(path, snippet)
        if inferred_role == 'UI component':
            reasons.append('contains user-facing interaction or presentation logic')
        elif inferred_role == 'Type definition':
            reasons.append('defines shared types consumed across modules')
        elif inferred_role == 'Configuration':
            reasons.append('captures configuration or environment-facing behavior')

    if not reasons:
        return None

    seen = set()
    deduped = []
    for reason in reasons:
        if reason in seen:
            continue
        seen.add(reason)
        deduped.append(reason)
    return ', '.join(deduped[:3])


def focus_preview_on_query(preview: str | None, query_intent: dict) -> str | None:
    if not preview:
        return preview

    exact_terms = set(query_intent.get('terms', []))
    keyword_terms = set(query_intent.get('keywords', []))
    if not exact_terms and not keyword_terms:
        return preview

    lines = preview.splitlines()
    if len(lines) <= 1:
        return preview

    best_index = 0
    best_score = 0
    for index, line in enumerate(lines):
        line_terms = set(extract_text_terms(line))
        score = len(line_terms & keyword_terms) + len(line_terms & exact_terms) * 2
        if score > best_score:
            best_index = index
            best_score = score

    if best_score <= 0 or best_index == 0:
        return preview

    return '\n'.join(lines[best_index:]).strip()


def build_read_snippets(
    snippet_items: list[dict],
    representative_snippets: list[dict],
    query_intent: dict,
) -> list[dict]:
    snippets = []
    seen = set()

    for item in snippet_items[:10]:
        preview = focus_preview_on_query(item.get('preview') or item.get('snippet'), query_intent)
        path = item.get('path')
        start_line = item.get('startLine')
        end_line = item.get('endLine')
        if not path or not preview:
            continue
        key = (path, start_line, end_line, preview)
        if key in seen:
            continue
        seen.add(key)
        snippets.append({
            'path': path,
            'kind': item.get('kind'),
            'startLine': start_line,
            'endLine': end_line,
            'preview': preview,
            'signals': item.get('signals', []),
            'score': item.get('score'),
            'whyMatched': item.get('reasons') or item.get('reason'),
        })

    if snippets:
        return snippets

    for item in representative_snippets[:8]:
        preview = focus_preview_on_query(item.get('snippet'), query_intent)
        key = (item.get('path'), item.get('startLine'), item.get('endLine'), preview)
        if key in seen:
            continue
        seen.add(key)
        snippets.append({
            'path': item.get('path'),
            'kind': 'representative',
            'startLine': item.get('startLine'),
            'endLine': item.get('endLine'),
            'preview': preview,
            'signals': [],
            'score': None,
            'whyMatched': item.get('reason'),
        })

    return snippets


def build_read_flow_anchors(
    file_paths: list[str],
    snippet_items: list[dict],
    query_intent: dict,
    limit: int,
) -> list[dict]:
    anchors = []
    seen = set()

    def classify_anchor(path: str, kind: str, preview: str = '') -> tuple[str | None, int]:
        lowered = (path or '').lower()
        if lowered.endswith('index.ts') or lowered.endswith('main.ts') or lowered.endswith('app.tsx'):
            return 'entry', 0
        if 'manager' in lowered:
            return 'manager', 1
        if 'deliveryroute' in lowered or 'route' in lowered or 'router' in lowered or 'dispatch' in lowered:
            return 'routing', 2
        if 'handler' in lowered:
            return 'handler', 3
        if 'store' in lowered:
            return 'store', 4
        if any(token in lowered for token in ['gateway', 'adapter', 'connector', 'plugin', 'transport']):
            return 'integration', 5
        if any(token in lowered for token in ['runtime', 'session', 'channel', 'service']):
            return 'runtime', 6
        if 'type' in lowered or '.d.ts' in lowered or 'schema' in lowered or 'model' in lowered:
            return 'types', 7
        if kind == 'function':
            return 'implementation', 8
        return None, 99

    for item in snippet_items:
        path = item.get('path')
        if not path:
            continue
        anchor_type, priority = classify_anchor(
            path,
            item.get('kind') or '',
            item.get('preview') or item.get('snippet') or '',
        )
        if not anchor_type:
            continue
        key = (path, anchor_type)
        if key in seen:
            continue
        seen.add(key)
        raw_reason = item.get('reasons') or item.get('reason') or []
        if isinstance(raw_reason, list):
            reason = ', '.join(raw_reason[:2])
        else:
            reason = str(raw_reason)
        anchors.append({
            'type': anchor_type,
            'path': path,
            'startLine': item.get('startLine'),
            'endLine': item.get('endLine'),
            'kind': item.get('kind'),
            'reason': reason,
            '_priority': priority,
        })

    for path in file_paths:
        anchor_type, priority = classify_anchor(path, '')
        if not anchor_type:
            continue
        key = (path, anchor_type)
        if key in seen:
            continue
        seen.add(key)
        anchors.append({
            'type': anchor_type,
            'path': path,
            'startLine': None,
            'endLine': None,
            'kind': 'file',
            'reason': 'selected as high-value file for this flow',
            '_priority': priority,
        })

    anchors.sort(key=lambda item: (item['_priority'], item['path'], item.get('startLine') or 0))
    return [{key: value for key, value in item.items() if key != '_priority'} for item in anchors[:limit]]


def build_read_next_hops(
    snapshot: dict,
    file_paths: list[str],
    snippet_items: list[dict],
    query_intent: dict,
) -> list[dict]:
    graph = snapshot.get('graph', {})
    important_files = snapshot.get('importantFiles', [])
    important_by_path = {item['path']: item for item in important_files}
    hotspot_by_path = {item['path']: item for item in graph.get('hotspots', [])}
    dependency_map = {
        item['path']: item['dependsOn']
        for item in graph.get('fileDependencies', [])
    }
    module_file_map = {
        item.get('module'): [file_item.get('path') for file_item in item.get('files', []) if file_item.get('path')]
        for item in graph.get('pathIndex', [])
    }
    next_hops = []
    seen = set(file_paths)
    matched_paths = [item.get('path') for item in snippet_items if item.get('path')]
    query_terms = set(query_intent.get('keywords', []))

    def path_module(path: str) -> str:
        return infer_path_module(path)

    def add_hop(path: str, reason: str) -> None:
        path = normalize_rel_path(path)
        if not path or path in seen:
            return
        seen.add(path)
        important = important_by_path.get(path, {})
        hotspot = hotspot_by_path.get(path, {})
        inferred_role = infer_read_file_role(path, {})
        why_important = important.get('whyImportant')
        if not why_important:
            fragments = []
            if hotspot.get('inbound') or hotspot.get('outbound'):
                fragments.append(f"hotspot in={hotspot.get('inbound', 0)} out={hotspot.get('outbound', 0)}")
            if hotspot.get('signals'):
                fragments.append(f"signals={hotspot.get('signals', 0)}")
            if inferred_role:
                fragments.append(inferred_role.lower())
            why_important = ', '.join(fragments) if fragments else 'related follow-up file'
        next_hops.append({
            'path': path,
            'reason': reason,
            'role': inferred_role or important.get('role'),
            'whyImportant': why_important,
        })

    for path in matched_paths[:6]:
        for dependency in dependency_map.get(path, [])[:4]:
            add_hop(dependency, 'matched file dependency')

    matched_modules = {path_module(path) for path in matched_paths + file_paths if path}
    for module_name in matched_modules:
        for path in module_file_map.get(module_name, [])[:8]:
            add_hop(path, 'same module follow-up')
            if len(next_hops) >= 8:
                break
        if len(next_hops) >= 8:
            break

    for path in snapshot.get('summary', {}).get('entryPoints', [])[:8]:
        add_hop(path, 'entry point follow-up')
        if len(next_hops) >= 8:
            break

    if query_terms:
        for item in important_files:
            lowered = item['path'].lower()
            if any(keyword in lowered for keyword in query_terms):
                add_hop(item['path'], 'keyword-related important file')
                if len(next_hops) >= 8:
                    break

    if len(next_hops) < 8:
        hotspot_candidates = sorted(
            graph.get('hotspots', []),
            key=lambda item: (-(item.get('inbound', 0) + item.get('outbound', 0)), item.get('path') or ''),
        )
        for item in hotspot_candidates:
            add_hop(item.get('path') or '', 'structural hotspot follow-up')
            if len(next_hops) >= 8:
                break

    return next_hops[:8]


def build_read_search_scope(snapshot: dict, file_paths: list[str]) -> dict:
    include_paths = []
    for path in file_paths[:8]:
        if path not in include_paths:
            include_paths.append(path)

    include_paths.extend(
        path for path in snapshot.get('contextHints', {}).get('readOrder', [])[:4]
        if path not in include_paths
    )

    return {
        'preferPaths': include_paths[:10],
        'excludePaths': [
            'repo/progress/',
            'node_modules/',
            'dist/',
            'build/',
            '__pycache__/',
        ],
        'notes': [
            'Prefer read-payload files before repo-wide search.',
            'Exclude generated caches and snapshot artifacts from code search.',
            'If more context is needed, follow nextHops before widening scope.',
        ],
    }


def summarize_external_context(external_context: dict) -> dict:
    return {
        'recentChangedFiles': external_context.get('recentChangedFiles', [])[:10],
        'documentationSources': external_context.get('documentationSources', [])[:10],
        'decisionSources': external_context.get('decisionSources', [])[:10],
        'teamConventions': external_context.get('teamConventions', [])[:8],
    }


def scan_files(project_path: str) -> list[str]:
    """Recursively scan project files, excluding defined directories."""
    files = []
    base = Path(project_path)

    for root, dirs, filenames in os.walk(base):
        rel_root = os.path.relpath(root, base)
        rel_root = '' if rel_root == '.' else normalize_rel_path(rel_root)

        # Filter out excluded directories in-place
        filtered_dirs = []
        for dir_name in dirs:
            if is_generated_env_dir(dir_name):
                continue
            rel_dir = dir_name if not rel_root else f'{rel_root}/{dir_name}'
            if is_excluded_path(rel_dir):
                continue
            filtered_dirs.append(dir_name)
        dirs[:] = filtered_dirs

        for filename in filenames:
            full_path = os.path.join(root, filename)
            rel_path = normalize_rel_path(os.path.relpath(full_path, base))
            if is_excluded_path(rel_path):
                continue
            files.append(full_path)

    return files


def detect_framework(files: list[str], project_path: str) -> list[str]:
    """Detect frameworks from package.json and file indicators."""
    frameworks = []
    base = Path(project_path)

    # Check package.json
    pkg_path = base / 'package.json'
    if pkg_path.exists():
        try:
            import json
            with open(pkg_path, 'r', encoding='utf-8') as f:
                pkg = json.load(f)
            deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
            for dep, name in FRAMEWORK_DEPS.items():
                if dep in deps and name not in frameworks:
                    frameworks.append(name)
        except Exception:
            pass

    # Check other files
    for f in files:
        fname = os.path.basename(f)
        if fname == 'manage.py' and 'Django' not in frameworks:
            frameworks.append('Django')
        elif fname == 'go.mod' and 'Go' not in frameworks:
            frameworks.append('Go')
        elif fname == 'Cargo.toml' and 'Rust' not in frameworks:
            frameworks.append('Rust')
        elif fname == 'pom.xml' and 'Maven' not in frameworks:
            frameworks.append('Maven')
        elif fname == 'build.gradle' and 'Gradle' not in frameworks:
            frameworks.append('Gradle')

    return frameworks


def find_entry_points(files: list[str], project_path: str) -> list[str]:
    """Find entry point files."""
    base = Path(project_path)
    entry_points = []

    for pattern in ENTRY_PATTERNS:
        for f in files:
            if os.path.basename(f) == pattern:
                rel = os.path.relpath(f, base)
                if rel not in entry_points:
                    entry_points.append(rel)

    return entry_points


def extract_api_routes(content: str, filename: str) -> list[dict]:
    """Extract API routes from file content."""
    routes = []
    ext = os.path.splitext(filename)[1]
    cleaned = clean_content_for_parsing(content, ext)

    if ext in ['.ts', '.js', '.tsx', '.jsx']:
        # Express routes: router.get('/path', handler)
        express_pattern = r'router\.(get|post|put|delete|patch|head|options)\s*\(\s*[\'"]([^\'"]+)[\'"]'
        for match in re.finditer(express_pattern, cleaned, re.IGNORECASE):
            routes.append({
                'method': match.group(1).upper(),
                'path': match.group(2)
            })

        # NestJS decorators: @Get('path'), @Post('path')
        nestjs_pattern = r'^\s*@(Get|Post|Put|Delete|Patch|Head|Options)\s*\(\s*[\'"]([^\'"]+)[\'"]'
        for match in re.finditer(nestjs_pattern, cleaned, re.IGNORECASE | re.MULTILINE):
            routes.append({
                'method': match.group(1).upper(),
                'path': match.group(2)
            })

        # FastAPI: @app.get('/path')
        fastapi_pattern = r'^\s*@(app|router)\.(get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]'
        for match in re.finditer(fastapi_pattern, cleaned, re.IGNORECASE | re.MULTILINE):
            routes.append({
                'method': match.group(2).upper(),
                'path': match.group(3)
            })

    elif ext == '.py':
        # FastAPI/Python decorators
        fastapi_pattern = r'^\s*@(app|router)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'
        for match in re.finditer(fastapi_pattern, cleaned, flags=re.MULTILINE):
            routes.append({
                'method': match.group(2).upper(),
                'path': match.group(3)
            })

        # Flask routes
        flask_pattern = (
            r'^\s*@(app|blueprint)\.route\(\s*["\']([^"\']+)["\']'
            r'(?P<args>[^)]*)\)'
        )
        for match in re.finditer(flask_pattern, cleaned, flags=re.MULTILINE):
            methods = re.search(r'methods\s*=\s*\[([^\]]+)\]', match.group('args'))
            if not methods:
                routes.append({
                    'method': 'GET',
                    'path': match.group(2)
                })
                continue

            for raw_method in re.findall(r'["\']([A-Za-z]+)["\']', methods.group(1)):
                routes.append({
                    'method': raw_method.upper(),
                    'path': match.group(2)
                })

    return routes


def extract_data_models(content: str, filename: str) -> list[dict]:
    """Extract data models from file content."""
    models = []
    ext = os.path.splitext(filename)[1]
    cleaned = clean_content_for_parsing(content, ext)

    if ext in ['.ts', '.tsx', '.js', '.jsx']:
        # TypeScript interfaces
        for match in re.finditer(r'(?:export\s+)?interface\s+(\w+)', cleaned):
            models.append({'name': match.group(1), 'type': 'interface'})

        # TypeScript types
        for match in re.finditer(r'(?:export\s+)?type\s+(\w+)\s*=', cleaned):
            models.append({'name': match.group(1), 'type': 'type'})

        # TypeScript classes
        for match in re.finditer(r'(?:export\s+)?class\s+(\w+)', cleaned):
            models.append({'name': match.group(1), 'type': 'class'})

    elif ext == '.py':
        # Pydantic models
        for match in re.finditer(r'class\s+(\w+)\s*\(\s*BaseModel', cleaned):
            models.append({'name': match.group(1), 'type': 'pydantic'})

        # Django models
        for match in re.finditer(r'class\s+(\w+)\s*\(\s*models\.Model', cleaned):
            models.append({'name': match.group(1), 'type': 'django-model'})

        # SQLAlchemy models
        for match in re.finditer(r'class\s+(\w+)\s*\(\s*Base', cleaned):
            models.append({'name': match.group(1), 'type': 'sqlalchemy'})

    return models


def extract_key_functions(content: str, filename: str) -> list[dict]:
    """Extract exported functions and classes."""
    functions = []
    ext = os.path.splitext(filename)[1]
    lines = content.split('\n')

    if ext in ['.ts', '.tsx', '.js', '.jsx']:
        # Function declarations
        for i, line in enumerate(lines):
            # export function name()
            match = re.search(r'export\s+(?:async\s+)?function\s+(\w+)', line)
            if match:
                functions.append({'name': match.group(1), 'file': filename, 'line': i + 1})
                continue

            # const/let name = async () => {} or const/let name = () => {}
            match = re.search(r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(', line)
            if match:
                name = match.group(1)
                if name not in ['if', 'for', 'while', 'switch', 'catch']:
                    functions.append({'name': name, 'file': filename, 'line': i + 1})

    elif ext == '.py':
        # def function_name
        for i, line in enumerate(lines):
            match = re.search(r'def\s+(\w+)\s*\(', line)
            if match:
                name = match.group(1)
                if not name.startswith('_'):
                    functions.append({'name': name, 'file': filename, 'line': i + 1})

    return functions


def infer_architecture(files: list[str], project_path: str) -> str:
    """Infer architecture from directory structure."""
    dirs = set()
    base = Path(project_path)

    for f in files:
        rel = normalize_rel_path(os.path.relpath(f, base))
        parts = Path(rel).parts
        for part in parts[:-1]:
            dirs.add(part.lower())

    for mode, patterns, arch in ARCHITECTURE_RULES:
        if mode == 'all' and all(pattern in dirs for pattern in patterns):
            return arch
        if mode == 'any' and any(pattern in dirs for pattern in patterns):
            return arch

    return 'Modular'


def build_file_tree(files: list[str], project_path: str) -> dict[str, list[str]]:
    """Build hierarchical file tree."""
    tree = {}
    base = Path(project_path)

    for f in files:
        rel = normalize_rel_path(os.path.relpath(f, base))
        parts = Path(rel).parts

        if len(parts) == 1:
            tree.setdefault('./', []).append(parts[0])
            continue

        dir_path = '/'.join(parts[:-1]) + '/'
        filename = parts[-1]

        if dir_path not in tree:
            tree[dir_path] = []
        tree[dir_path].append(filename)

    return {
        dir_path: sorted(filenames)
        for dir_path, filenames in sorted(tree.items())
    }


def generate_snapshot(project_path: str, force: bool = False) -> dict:
    """Generate complete project snapshot."""
    base = Path(project_path)
    output_dir = base / 'repo' / 'progress'
    output_file = output_dir / SNAPSHOT_FILENAME
    index_state_file = output_dir / INDEX_STATE_FILENAME

    # Scan files
    files = scan_files(project_path)
    current_signatures = build_file_signatures(files, project_path)
    source_fingerprint = build_source_fingerprint(current_signatures)
    newest_source_mtime = get_newest_source_mtime(files)
    existing_snapshot = load_existing_snapshot(resolve_snapshot_file(output_dir))
    existing_index_state = load_existing_index_state(resolve_index_state_file(output_dir))

    if (
        existing_snapshot
        and not force
        and existing_snapshot.get('version') == SNAPSHOT_VERSION
        and existing_snapshot.get('sourceFingerprint') == source_fingerprint
    ):
        cached_chunks = (existing_index_state or {}).get('chunks', [])
        freshness = existing_snapshot.setdefault('freshness', {})
        freshness['stale'] = False
        freshness['reason'] = 'source fingerprint unchanged'
        freshness['newestSourceMtime'] = newest_source_mtime
        existing_snapshot['index'] = build_index_metadata(
            base,
            index_state_file,
            existing_index_state,
            current_signatures,
            cached_chunks,
            reusing_snapshot=True,
        )
        existing_snapshot['chunkCatalog'] = build_chunk_catalog(
            cached_chunks,
            existing_snapshot.get('importantFiles', []),
        )
        write_snapshot(output_file, existing_snapshot, chunks=cached_chunks)
        return existing_snapshot

    file_records, total_lines = collect_file_records(files, project_path)

    # Threading: submit git stats early (I/O-bound subprocess calls), overlap with CPU work
    _git_stats_executor = ThreadPoolExecutor(max_workers=2)
    try:
        _git_future = _git_stats_executor.submit(
            collect_git_stats, project_path, [r['path'] for r in file_records]
        )

        # Detect framework
        frameworks = detect_framework(files, project_path)

        for record in file_records:
            for framework_hint in record.get('frameworkHints', []):
                if framework_hint not in frameworks:
                    frameworks.append(framework_hint)

        # Find entry points
        entry_points = find_entry_points(files, project_path)
        dependencies = extract_dependencies(project_path)
        workspace = detect_workspace(file_records, project_path, dependencies)
        important_files = build_important_files(file_records, entry_points, workspace)
        modules = summarize_modules_from_records(file_records)
        analysis = build_analysis_metadata(file_records)
        chunks = build_chunks(file_records)

        chunk_catalog = build_chunk_catalog(chunks, important_files)
        index_metadata = build_index_metadata(
            base,
            index_state_file,
            existing_index_state,
            current_signatures,
            chunks,
            reusing_snapshot=False,
        )

        # Expand framework hints from dependency manifests
        for manifest_path, manifest_dependencies in dependencies.items():
            if manifest_path.endswith(('requirements.txt', 'pyproject.toml')):
                python_frameworks = {
                    'fastapi': 'FastAPI',
                    'flask': 'Flask',
                    'django': 'Django',
                    'pydantic': 'Pydantic',
                    'sqlalchemy': 'SQLAlchemy',
                }
                for dependency_name, framework_name in python_frameworks.items():
                    if dependency_name in manifest_dependencies and framework_name not in frameworks:
                        frameworks.append(framework_name)
        frameworks = sorted(set(frameworks))
        summary = build_summary(
            project_path,
            files,
            frameworks,
            entry_points,
            total_lines,
            file_records,
            important_files,
        )
        context_hints = build_context_hints(summary, workspace, important_files, modules)

        # Extract API routes, data models, functions
        api_routes = []
        data_models = []
        key_functions = []

        for record in file_records:
            for route in record['apiRoutes']:
                api_routes.append({
                    'method': route['method'],
                    'path': route['path'],
                    'handler': record['path'],
                    'line': route.get('line'),
                    'source': record.get('analysisEngine'),
                    'confidence': record.get('analysisConfidence'),
                })

            for model in record['dataModels']:
                data_models.append({
                    'name': model['name'],
                    'type': model['type'],
                    'file': record['path'],
                    'line': model.get('line'),
                    'source': record.get('analysisEngine'),
                    'confidence': record.get('analysisConfidence'),
                })

            for func in record['keyFunctions']:
                key_functions.append(func)

        # Deduplicate
        seen_routes = set()
        unique_routes = []
        for r in api_routes:
            key = f"{r['method']}:{r['path']}:{r['handler']}"
            if key not in seen_routes:
                seen_routes.add(key)
                unique_routes.append(r)

        seen_models = set()
        unique_models = []
        for m in data_models:
            key = f"{m['name']}:{m['type']}:{m['file']}"
            if key not in seen_models:
                seen_models.add(key)
                unique_models.append(m)

        seen_functions = set()
        unique_functions = []
        for func in key_functions:
            key = f"{func['file']}:{func['name']}:{func['line']}"
            if key not in seen_functions:
                seen_functions.add(key)
                unique_functions.append(func)

        # Limit key functions after ranking important areas first
        key_functions = sorted(unique_functions, key=lambda item: rank_key_function(item, entry_points))[:80]

        # Infer architecture
        architecture = infer_architecture(files, project_path)
        graph = build_code_graph(file_records, unique_routes, unique_models, key_functions, workspace, Path(project_path))
        external_context = collect_external_context(project_path, file_records)

        # Collect git stats (submitted early, wait for result now)
        git_stats = {}
        try:
            git_stats = _git_future.result()
            if git_stats:
                chunks = enrich_chunks_with_git(chunks, git_stats)
        except Exception:
            pass
    finally:
        _git_stats_executor.shutdown(wait=False)

    retrieval, context_packs = build_retrieval_artifacts(chunks, important_files, graph, external_context)

    # Build fuzzy symbol index
    fuzzy_searcher = FuzzySymbolSearcher()
    fuzzy_searcher.build_index(chunks)

    # Build snapshot
    snapshot = {
        'version': SNAPSHOT_VERSION,
        'generatedAt': utc_now_iso(),
        'projectPath': str(base.resolve()),
        'sourceFingerprint': source_fingerprint,
        'freshness': {
            'stale': False,
            'reason': 'forced regeneration' if force else ('regenerated because sources changed' if existing_snapshot else 'initial generation'),
            'newestSourceMtime': newest_source_mtime,
            'snapshotPath': normalize_rel_path(str(output_file.relative_to(base))),
        },
        'git': collect_git_context(project_path),
        'summary': summary,
        'workspace': workspace,
        'analysis': analysis,
        'index': index_metadata,
        'contextHints': context_hints,
        'fileTree': build_file_tree(files, project_path),
        'modules': modules,
        'dependencies': dependencies,
        'importantFiles': important_files,
        'chunkCatalog': chunk_catalog,
        'graph': graph,
        'retrieval': retrieval,
        'contextPacks': context_packs,
        'externalContext': external_context,
        'representativeSnippets': build_representative_snippets(file_records, important_files),
        'apiRoutes': sorted(unique_routes, key=lambda item: (item['handler'], item['path'], item['method'])),
        'dataModels': sorted(unique_models, key=lambda item: (item['file'], item['type'], item['name'])),
        'keyFunctions': key_functions,
        'architecture': architecture,
        'gitStats': git_stats,
        'symbolIndex': fuzzy_searcher.to_dict(),
    }

    # Save to file
    write_snapshot(output_file, snapshot, chunks=chunks)
    try:
        save_index_state(index_state_file, current_signatures, chunks, file_records, source_fingerprint)
    except Exception:
        print(f'Warning: index state save failed (snapshot is still valid)', file=sys.stderr)

    print(
        f"Snapshot saved to: {output_file}\n"
        f"  {total_lines:,} lines, {len(file_records):,} files, {len(chunks):,} chunks",
        file=sys.stderr,
    )
    return snapshot


def refresh_index(project_path: str) -> dict:
    base = Path(project_path)
    output_dir = base / 'repo' / 'progress'
    output_file = output_dir / SNAPSHOT_FILENAME
    index_state_file = output_dir / INDEX_STATE_FILENAME
    existing_snapshot = load_existing_snapshot(resolve_snapshot_file(output_dir))
    existing_index_state = load_existing_index_state(resolve_index_state_file(output_dir))

    if not existing_snapshot or not existing_index_state:
        return generate_snapshot(project_path, force=False)

    previous_files = existing_index_state.get('files', {})
    previous_commit = (existing_snapshot.get('git') or {}).get('commit')
    current_commit = run_git_command(project_path, ['rev-parse', 'HEAD'])
    git_status = run_git_command(project_path, ['status', '--porcelain'])

    # Fast path: when git commit is unchanged and worktree is clean, skip expensive
    # repo scan/signature rebuild and directly reuse cached snapshot + index.
    if (
        previous_commit
        and current_commit
        and previous_commit == current_commit
        and git_status is None
    ):
        cached_chunks = existing_index_state.get('chunks', [])
        existing_snapshot['generatedAt'] = utc_now_iso()
        existing_snapshot['sourceFingerprint'] = (
            existing_index_state.get('sourceFingerprint')
            or existing_snapshot.get('sourceFingerprint')
        )
        previous_freshness = existing_snapshot.get('freshness') or {}
        existing_snapshot['freshness'] = {
            'stale': False,
            'reason': 'incremental refresh skipped (git unchanged)',
            'newestSourceMtime': previous_freshness.get('newestSourceMtime'),
            'snapshotPath': normalize_rel_path(str(output_file.relative_to(base))),
            'hashedCandidateFiles': 0,
            'hashAuditCursor': previous_freshness.get('hashAuditCursor', 0),
        }
        existing_snapshot['index'] = build_index_metadata(
            base,
            index_state_file,
            existing_index_state,
            previous_files,
            cached_chunks,
            reusing_snapshot=True,
        )
        existing_snapshot['chunkCatalog'] = build_chunk_catalog(
            cached_chunks,
            existing_snapshot.get('importantFiles', []),
        )
        write_snapshot(output_file, existing_snapshot, chunks=cached_chunks)
        return existing_snapshot

    files = scan_files(project_path)
    audit_cursor = int((existing_snapshot.get('freshness') or {}).get('hashAuditCursor') or 0)
    current_signatures, hashed_candidate_paths, next_audit_cursor = build_incremental_file_signatures(
        files,
        project_path,
        previous_files,
        previous_commit=previous_commit,
        current_commit=current_commit,
        audit_cursor=audit_cursor,
    )
    source_fingerprint = build_source_fingerprint(current_signatures)
    newest_source_mtime = get_newest_source_mtime(files)
    previous_chunks = existing_index_state.get('chunks', [])
    previous_paths = set(previous_files.keys())
    current_paths = set(current_signatures.keys())
    removed_paths = previous_paths - current_paths
    changed_or_new_paths = {
        path for path in current_paths
        if path not in previous_files
        or not signature_matches(previous_files.get(path, {}), current_signatures.get(path, {}))
    }

    if not changed_or_new_paths and not removed_paths:
        existing_snapshot['generatedAt'] = utc_now_iso()
        existing_snapshot['sourceFingerprint'] = source_fingerprint
        existing_snapshot['freshness'] = {
            'stale': False,
            'reason': 'source fingerprint unchanged',
            'newestSourceMtime': newest_source_mtime,
            'snapshotPath': normalize_rel_path(str(output_file.relative_to(base))),
            'hashedCandidateFiles': len(hashed_candidate_paths),
            'hashAuditCursor': next_audit_cursor,
        }
        existing_snapshot['index'] = build_index_metadata(
            base,
            index_state_file,
            existing_index_state,
            current_signatures,
            previous_chunks,
            reusing_snapshot=True,
        )
        existing_snapshot['chunkCatalog'] = build_chunk_catalog(
            previous_chunks,
            existing_snapshot.get('importantFiles', []),
        )
        write_snapshot(output_file, existing_snapshot, chunks=previous_chunks)
        return existing_snapshot

    changed_files = [str(base / path) for path in sorted(changed_or_new_paths)]
    changed_records, _ = collect_file_records(changed_files, project_path)
    changed_chunks = build_chunks(changed_records)
    changed_payload = build_index_files_payload(current_signatures, changed_chunks, changed_records)

    next_chunks = [
        chunk for chunk in previous_chunks
        if chunk.get('path') not in changed_or_new_paths
        and chunk.get('path') not in removed_paths
    ]
    next_chunks.extend(changed_chunks)

    next_files_payload = {
        path: meta for path, meta in previous_files.items()
        if path not in changed_or_new_paths and path not in removed_paths and path in current_signatures
    }
    next_files_payload.update(changed_payload)

    next_index_state = {
        'version': INDEX_STATE_VERSION,
        'generatedAt': utc_now_iso(),
        'sourceFingerprint': source_fingerprint,
        'files': next_files_payload,
        'chunks': next_chunks,
    }
    save_index_state_payload(index_state_file, next_index_state)

    existing_snapshot['generatedAt'] = utc_now_iso()
    existing_snapshot['sourceFingerprint'] = source_fingerprint
    existing_snapshot['freshness'] = {
        'stale': False,
        'reason': 'incremental index refreshed',
        'newestSourceMtime': newest_source_mtime,
        'snapshotPath': normalize_rel_path(str(output_file.relative_to(base))),
        'hashedCandidateFiles': len(hashed_candidate_paths),
        'hashAuditCursor': next_audit_cursor,
    }
    existing_snapshot['index'] = build_index_metadata(
        base,
        index_state_file,
        existing_index_state,
        current_signatures,
        next_chunks,
        reusing_snapshot=True,
    )
    existing_snapshot['chunkCatalog'] = build_chunk_catalog(
        next_chunks,
        existing_snapshot.get('importantFiles', []),
    )
    write_snapshot(output_file, existing_snapshot, chunks=next_chunks)
    return existing_snapshot


def read_query_input(
    inline_query: str | None = None,
    escaped_query: str | None = None,
    query_file: str | None = None,
    use_stdin: bool = False,
) -> str | None:
    if escaped_query:
        raw = escaped_query.strip()
        if not raw:
            return None
        # `--query-escaped` is commonly used with ascii escape sequences (\uXXXX).
        # If no backslash escape marker is present, treat it as plain text to avoid
        # corrupting already-decoded unicode input.
        if '\\' not in raw:
            return raw
        try:
            decoded = codecs.decode(raw, 'unicode_escape').strip()
            return decoded or raw
        except Exception:
            return raw

    if query_file:
        query_path = Path(query_file)
        if not query_path.exists():
            raise FileNotFoundError(f'Query file not found: {query_file}')
        return query_path.read_text(encoding='utf-8-sig').strip() or None

    if use_stdin:
        stdin_buffer = getattr(sys.stdin, 'buffer', None)
        if stdin_buffer is not None:
            payload = stdin_buffer.read()
            text, _encoding = decode_text_bytes(payload)
            return text.strip() or None if text else None
        return sys.stdin.read().strip() or None

    return inline_query


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python generate.py <project_path> [refresh|--refresh|read|--read|report|--report] "
            "[--task <task>] [--query <query> | --query-escaped <ascii_escaped_query> "
            "| --query-file <utf8_file> | --query-stdin] "
            "[--semantic] [--incremental] [--sqlite] [--no-sqlite]",
            file=sys.stderr,
        )
        sys.exit(1)

    project_path = sys.argv[1]
    cli_args = sys.argv[2:]
    read_mode = '--read' in cli_args or (len(cli_args) > 0 and cli_args[0] == 'read')
    report_mode = '--report' in cli_args or (len(cli_args) > 0 and cli_args[0] == 'report')
    refresh_mode = (
        '--refresh' in cli_args
        or (len(cli_args) > 0 and cli_args[0] == 'refresh')
    )
    task = 'understand-project'
    query = None
    escaped_query = None
    query_file = None
    query_stdin = '--query-stdin' in cli_args

    # Advanced chunking mode flags
    global USE_SEMANTIC_CHUNKING, USE_INCREMENTAL_MODE, USE_SQLITE_INDEX
    USE_SEMANTIC_CHUNKING = '--semantic' in cli_args
    USE_INCREMENTAL_MODE = '--incremental' in cli_args
    USE_SQLITE_INDEX = '--no-sqlite' not in cli_args

    if '--task' in cli_args:
        task_index = cli_args.index('--task')
        if task_index + 1 < len(cli_args):
            task = cli_args[task_index + 1]

    if '--query' in cli_args:
        query_index = cli_args.index('--query')
        if query_index + 1 < len(cli_args):
            query = cli_args[query_index + 1]

    if '--query-escaped' in cli_args:
        escaped_query_index = cli_args.index('--query-escaped')
        if escaped_query_index + 1 < len(cli_args):
            escaped_query = cli_args[escaped_query_index + 1]

    if '--query-file' in cli_args:
        query_file_index = cli_args.index('--query-file')
        if query_file_index + 1 < len(cli_args):
            query_file = cli_args[query_file_index + 1]

    if not os.path.isdir(project_path):
        print(f"Error: {project_path} is not a valid directory", file=sys.stderr)
        sys.exit(1)

    try:
        query = read_query_input(query, escaped_query, query_file, query_stdin)
    except FileNotFoundError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    if (
        query
        and '--query' in cli_args
        and not escaped_query
        and not query_file
        and not query_stdin
        and any(ord(ch) > 127 for ch in query)
        and os.name == 'nt'
    ):
        print(
            'Warning: non-ASCII query detected on raw --query; prefer --query-file, --query-escaped, or --query-stdin on Windows.',
            file=sys.stderr,
        )

    if report_mode:
        base = Path(project_path)
        progress_dir = base / 'repo' / 'progress'
        sqlite_db_path = str(resolve_sqlite_file(progress_dir))
        snapshot = load_existing_snapshot(resolve_snapshot_file(progress_dir))
        if not snapshot or refresh_mode:
            snapshot = refresh_index(project_path) if refresh_mode else generate_snapshot(project_path, force=False)

        index_state = load_existing_index_state(resolve_index_state_file(progress_dir))
        write_json_stdout(build_report_payload(snapshot, index_state, task, query, sqlite_db_path=sqlite_db_path))
        return

    if read_mode:
        base = Path(project_path)
        progress_dir = base / 'repo' / 'progress'
        sqlite_db_path = str(resolve_sqlite_file(progress_dir))
        snapshot = load_existing_snapshot(resolve_snapshot_file(progress_dir))
        if not snapshot and not refresh_mode:
            print(
                "Error: snapshot not found. Run /context-codebase or /context-codebase refresh first.",
                file=sys.stderr,
            )
            sys.exit(1)
        if refresh_mode:
            snapshot = refresh_index(project_path)
        if snapshot is None:
            print(
                "Error: snapshot not found after refresh attempt.",
                file=sys.stderr,
            )
            sys.exit(1)

        index_state = load_existing_index_state(resolve_index_state_file(progress_dir))
        write_json_stdout(build_read_payload(snapshot, index_state, task, query, sqlite_db_path=sqlite_db_path))
        return

    snapshot = refresh_index(project_path) if refresh_mode else generate_snapshot(project_path, force=False)

    if query:
        progress_dir = Path(project_path) / 'repo' / 'progress'
        index_state = load_existing_index_state(resolve_index_state_file(progress_dir))
        sqlite_db_path = str(resolve_sqlite_file(progress_dir))
        focus_pack = build_focus_context_pack(query, task, snapshot, index_state, sqlite_db_path=sqlite_db_path)
        write_json_stdout(focus_pack or snapshot)
        return

    write_json_stdout(snapshot)


def write_json_stdout(payload: dict) -> None:
    text = json.dumps(payload, indent=2, ensure_ascii=False) + '\n'
    buffer = getattr(sys.stdout, 'buffer', None)
    if buffer is not None:
        buffer.write(text.encode('utf-8'))
        buffer.flush()
        return

    try:
        sys.stdout.write(text)
    except UnicodeEncodeError:
        safe_text = text.encode('ascii', errors='backslashreplace').decode('ascii')
        sys.stdout.write(safe_text)


if __name__ == '__main__':
    main()
