#!/usr/bin/env python3
"""
miloya-codebase: Generate project snapshot JSON
Usage: python generate.py <project_path> [--force]
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import codecs
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from context_engine.analyzers import AnalyzerRegistry
from context_engine.external_context import collect_external_context
from context_engine.graph import build_code_graph
from context_engine.retrieval import build_retrieval_artifacts, retrieve_chunks

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None


SNAPSHOT_VERSION = '3.0'
INDEX_STATE_VERSION = '1.0'
MAX_TEXT_FILE_BYTES = 512 * 1024
MAX_IMPORTANT_FILES = 15
MAX_REPRESENTATIVE_SNIPPETS = 5
MAX_SNIPPET_LINES = 12
MAX_CHUNK_LINES = 60
MAX_CHUNK_PREVIEW_LINES = 16
MAX_CHUNK_CATALOG_ITEMS = 40

EXCLUDE_DIRS = {
    'node_modules', '.git', 'dist', 'build', 'venv', '__pycache__',
    '.venv', 'env', '.env', 'coverage', '.next', '.nuxt', '.cache',
    '.svn', '.hg', 'vendor', 'target', 'out', '.idea', '.vscode'
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


def is_excluded_path(rel_path: str) -> bool:
    normalized = normalize_rel_path(rel_path).strip('./')
    if not normalized:
        return False

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
    if '/tests/' in file_path.lower() or file_name.startswith('test_') or file_name.endswith('_test.py'):
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

    try:
        return path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return None
    except Exception:
        return None


def build_source_fingerprint(files: list[str], project_path: str) -> str:
    base = Path(project_path)
    digest = hashlib.sha256()

    for file_path in files:
        path_obj = Path(file_path)
        rel_path = normalize_rel_path(os.path.relpath(file_path, base))
        stat = path_obj.stat()
        digest.update(f'{rel_path}:{stat.st_size}:{stat.st_mtime_ns}\n'.encode('utf-8'))

    return digest.hexdigest()


def build_file_signatures(files: list[str], project_path: str) -> dict[str, dict]:
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
            text=True,
            check=True,
        )
    except Exception:
        return None

    return completed.stdout.strip() or None


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


def collect_file_records(files: list[str], project_path: str) -> tuple[list[dict], int]:
    base = Path(project_path)
    records = []
    total_lines = 0

    for file_path in files:
        path_obj = Path(file_path)
        rel_path = normalize_rel_path(os.path.relpath(file_path, base))
        language = detect_language(rel_path)
        content = read_text_file(path_obj)
        line_count = len(content.splitlines()) if content is not None else 0
        total_lines += line_count
        analysis = ANALYZER_REGISTRY.analyze_file(content, rel_path, project_path)

        records.append({
            'path': rel_path,
            'fileName': path_obj.name,
            'language': language,
            'lineCount': line_count,
            'sizeBytes': path_obj.stat().st_size,
            'content': content,
            'imports': analysis.imports,
            'exports': analysis.exports,
            'apiRoutes': analysis.api_routes,
            'dataModels': analysis.data_models,
            'keyFunctions': analysis.key_functions,
            'frameworkHints': analysis.framework_hints,
            'analysisEngine': analysis.engine,
            'analysisConfidence': analysis.confidence,
            'analysisWarnings': analysis.warnings,
        })

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

    if '/tests/' in lower_path or record['fileName'].startswith('test_') or record['fileName'].endswith('_test.py'):
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
            anchor_lines.append((func['line'], 'function', [func['name']]))
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


def diff_index_state(previous_state: dict | None, current_signatures: dict[str, dict]) -> dict:
    previous_files = (previous_state or {}).get('files', {})
    previous_paths = set(previous_files.keys())
    current_paths = set(current_signatures.keys())

    new_paths = current_paths - previous_paths
    removed_paths = previous_paths - current_paths
    shared_paths = current_paths & previous_paths
    changed_paths = {
        path for path in shared_paths
        if {
            'sizeBytes': previous_files.get(path, {}).get('sizeBytes'),
            'mtimeNs': previous_files.get(path, {}).get('mtimeNs'),
        } != current_signatures.get(path, {})
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


def save_index_state(
    index_state_file: Path,
    current_signatures: dict[str, dict],
    chunks: list[dict],
    file_records: list[dict],
    source_fingerprint: str,
) -> None:
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

    payload = {
        'version': INDEX_STATE_VERSION,
        'generatedAt': utc_now_iso(),
        'sourceFingerprint': source_fingerprint,
        'files': files_payload,
        'chunks': chunks,
    }

    index_state_file.parent.mkdir(parents=True, exist_ok=True)
    index_state_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')


def load_existing_snapshot(output_file: Path) -> dict | None:
    if not output_file.exists():
        return None

    try:
        return json.loads(output_file.read_text(encoding='utf-8'))
    except Exception:
        return None


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
) -> dict | None:
    if not query or not index_state:
        return None

    chunks = index_state.get('chunks', [])
    if not chunks:
        return None

    graph = snapshot.get('graph', {})
    important_files = snapshot.get('importantFiles', [])
    external_context = snapshot.get('externalContext', {})
    important_ranks = {item['path']: index for index, item in enumerate(important_files)}
    recent_changed = set(external_context.get('recentChangedFiles', []))
    query_intent = infer_query_intent(query)
    expanded_query_terms = expand_query_terms_for_retrieval(
        query_intent,
        snapshot.get('retrieval', {}),
    )
    expanded_query = ' '.join(expanded_query_terms) or query
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
        limit=24,
    )
    matches = rerank_read_matches(matches, query_intent)[:12]
    related_paths = []
    for match in matches:
        related_paths.append(match['path'])
        related_paths.extend(file_dependency_map.get(match['path'], []))

    return {
        'task': task,
        'query': query,
        'matches': matches,
        'files': list(dict.fromkeys(related_paths))[:12],
    }


def expand_query_terms_for_retrieval(query_intent: dict, retrieval: dict) -> list[str]:
    expanded_terms = list(dict.fromkeys([
        *query_intent.get('terms', []),
        *query_intent.get('keywords', []),
    ]))
    related_terms = (retrieval.get('projectVocabulary') or {}).get('relatedTerms', {})

    for term in list(expanded_terms):
        for related in related_terms.get(term.lower(), [])[:4]:
            if related not in expanded_terms:
                expanded_terms.append(related)

    return expanded_terms[:36]


def build_read_payload(
    snapshot: dict,
    index_state: dict | None,
    task: str,
    query: str | None,
) -> dict:
    normalized_query = normalize_query_text(query)
    retrieval = snapshot.get('retrieval', {})
    available_tasks = retrieval.get('availableTasks', [])
    selected_task = task if task in available_tasks else retrieval.get('defaultTask', 'understand-project')
    quick_start = snapshot.get('contextHints', {})
    graph = snapshot.get('graph', {})
    important_files = snapshot.get('importantFiles', [])
    representative_snippets = snapshot.get('representativeSnippets', [])
    query_intent = infer_query_intent(normalized_query)
    read_profile = select_read_profile(query_intent)
    read_limits = determine_read_limits(query_intent)

    if normalized_query:
        focus_pack = build_focus_context_pack(normalized_query, selected_task, snapshot, index_state)
        snippet_items = (focus_pack or {}).get('matches', [])
        file_paths = (focus_pack or {}).get('files', [])
        task_description = describe_task(snapshot, selected_task)
    else:
        task_pack = snapshot.get('contextPacks', {}).get(selected_task, {})
        snippet_items = task_pack.get('chunks', [])
        file_paths = build_default_read_paths(snapshot, task_pack)
        task_description = task_pack.get('description') or describe_task(snapshot, selected_task)

    snippet_items = rerank_read_matches(snippet_items, query_intent, read_profile)
    file_paths = prioritize_read_file_paths(file_paths, snippet_items, query_intent, read_profile)
    file_paths = refine_read_file_paths(snapshot, file_paths, query_intent, read_profile)

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
        'taskDescription': task_description,
        'availableTasks': available_tasks,
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
        'searchScope': build_read_search_scope(snapshot, file_paths[:read_limits['files']]),
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


def build_report_payload(
    snapshot: dict,
    index_state: dict | None,
    task: str,
    query: str | None,
) -> dict:
    read_payload = build_read_payload(snapshot, index_state, task, query)
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


GENERAL_QUERY_TERM_EXPANSIONS = {
    'skill': ['skills'],
    'skills': ['skill'],
    'plugin': ['plugins', 'extension'],
    'display': ['screen', 'view', 'render'],
    'screen': ['display', 'view'],
    'encoder': ['codec'],
    'codec': ['encoder'],
    'fps': ['framerate', 'frame-rate', 'max-fps', 'frame', 'rate'],
    'framerate': ['fps', 'frame-rate', 'max-fps', 'frame', 'rate'],
    'bitrate': ['rate'],
    'resolution': ['width', 'height', 'size'],
    'select': ['selector', 'option', 'choose', 'preset', 'change'],
    'change': ['select', 'option', 'preset'],
    'runtime': ['flow', 'lifecycle', 'engine', 'adapter'],
    'lifecycle': ['runtime', 'flow'],
    'download': ['install', 'fetch', 'clone', 'archive', 'zip'],
    'install': ['download', 'setup', 'enable'],
    'delete': ['remove', 'cleanup'],
    'remove': ['delete', 'cleanup'],
    'load': ['read', 'parse', 'resolve'],
    'read': ['load', 'parse'],
    'list': ['scan', 'discover'],
    'config': ['setting', 'configure', 'options'],
    'setting': ['config', 'configure', 'options'],
    'route': ['routing', 'router', 'dispatch', 'delivery'],
    'routing': ['route', 'router', 'dispatch', 'delivery'],
    'gateway': ['adapter', 'connector', 'transport', 'channel'],
    'message': ['reply', 'send', 'receive', 'channel'],
    'store': ['persist', 'save', 'sqlite', 'db'],
    'persist': ['store', 'save', 'sqlite'],
    'type': ['types', 'interface', 'schema', 'model'],
    'types': ['type', 'interface', 'schema', 'model'],
    '配置': ['config', 'setting', 'configure', 'options'],
    '路由': ['route', 'routing', 'router', 'dispatch', 'delivery'],
    '网关': ['gateway', 'adapter', 'connector', 'transport', 'channel'],
    '消息': ['message', 'reply', 'send', 'receive', 'channel'],
    '存储': ['store', 'persist', 'save', 'sqlite', 'db'],
    '持久化': ['persist', 'store', 'save', 'sqlite'],
    '类型': ['type', 'types', 'interface', 'schema', 'model'],
    '界面': ['ui', 'component', 'page', 'view'],
    '组件': ['component', 'ui', 'view'],
    '显示': ['display', 'screen', 'view'],
    '帧率': ['fps', 'framerate', 'max-fps', 'frame', 'rate'],
    '编码器': ['encoder', 'codec'],
    '码率': ['bitrate', 'rate'],
    '比特率': ['bitrate', 'rate'],
    '分辨率': ['resolution', 'width', 'height', 'size'],
    '选择': ['select', 'selector', 'option', 'choose', 'preset', 'change'],
    '选项': ['option', 'select', 'preset'],
    '预设': ['preset', 'option', 'select'],
    '切换': ['toggle', 'switch', 'change', 'select'],
    '运行时': ['runtime', 'engine', 'adapter', 'flow'],
    '生命周期': ['lifecycle', 'runtime', 'flow'],
    '流程': ['flow', 'process', 'pipeline', 'lifecycle'],
    '实现': ['implementation', 'implement', 'logic'],
    '下载': ['download', 'install', 'fetch', 'clone', 'archive', 'zip'],
    '安装': ['install', 'setup', 'enable'],
    '删除': ['delete', 'remove', 'cleanup'],
    '读取': ['read', 'load', 'parse'],
    '加载': ['load', 'read', 'resolve'],
    '解析': ['parse', 'resolve'],
    '管理': ['manager', 'manage', 'management'],
    '技能': ['skill', 'skills'],
    '插件': ['plugin', 'plugins', 'extension'],
    '服务': ['service', 'services'],
    '处理': ['handler', 'process'],
    '会话': ['session'],
}

GENERAL_QUERY_ACTION_TERMS = {
    'download', 'install', 'delete', 'remove', 'load', 'read', 'list', 'scan',
    'discover', 'parse', 'resolve', 'sync', 'start', 'stop', 'save', 'persist',
    'dispatch', 'delivery', 'send', 'receive', 'reply', 'select', 'change',
    'choose', 'toggle', 'apply', 'set',
    '下载', '安装', '删除', '读取', '加载', '解析', '同步', '启动', '停止', '保存',
    '持久化', '分发', '投递', '发送', '接收', '回复', '选择', '切换', '修改', '设置',
}

PARAMETER_SELECTION_TERMS = {
    'fps', 'framerate', 'frame-rate', 'max-fps',
    'bitrate', 'rate', 'resolution', 'width', 'height', 'size',
    'encoder', 'codec', 'display', 'screen',
    '帧率', '码率', '比特率', '分辨率', '编码器', '显示',
}

UI_SELECTION_TERMS = {
    'select', 'selector', 'option', 'choose', 'preset', 'change', 'toggle',
    '设置', '选择', '选项', '预设', '切换', '修改',
}


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
        if re.fullmatch(r'[\u4e00-\u9fff]+', term):
            if len(term) <= 4 and term not in seen:
                seen.add(term)
                collected.append(term)
            for candidate in GENERAL_QUERY_TERM_EXPANSIONS:
                if candidate in term and candidate not in seen:
                    seen.add(candidate)
                    collected.append(candidate)
            continue

        if term not in seen:
            seen.add(term)
            collected.append(term)

    return collected[:24]


def expand_query_terms(terms: list[str]) -> list[str]:
    expanded: list[str] = []
    seen = set()

    for term in terms:
        if term not in seen:
            seen.add(term)
            expanded.append(term)
        for synonym in GENERAL_QUERY_TERM_EXPANSIONS.get(term, []):
            if synonym not in seen:
                seen.add(synonym)
                expanded.append(synonym)

    return expanded[:32]


def determine_read_limits(query_intent: dict) -> dict[str, int]:
    labels = set(query_intent.get('labels', []))
    keywords = set(query_intent.get('keywords', []))
    limits = {
        'files': 4,
        'snippets': 3,
        'nextHops': 2,
        'anchors': 4,
        'maxWords': 380,
    }

    if 'integration-flow' in labels or 'routing-flow' in labels:
        limits.update({
            'files': 4,
            'snippets': 3,
            'nextHops': 2,
            'anchors': 4,
            'maxWords': 420,
        })
    elif 'configuration' in labels or 'documentation-link' in labels:
        limits.update({
            'files': 4,
            'snippets': 3,
            'nextHops': 2,
            'anchors': 4,
            'maxWords': 380,
        })
    elif 'runtime-flow' in labels:
        limits.update({
            'files': 4,
            'snippets': 3,
            'nextHops': 2,
            'anchors': 4,
            'maxWords': 400,
        })

    if keywords & GENERAL_QUERY_ACTION_TERMS:
        limits['files'] = min(limits['files'], 4)
        limits['snippets'] = min(limits['snippets'], 3)

    return limits


def select_read_profile(query_intent: dict) -> dict:
    keyword_set = set(query_intent.get('keywords', []))
    exact_terms = set(query_intent.get('terms', []))
    action_terms = keyword_set & GENERAL_QUERY_ACTION_TERMS
    profile = {
        'name': 'generic',
        'focusManagerTokens': set(),
        'focusEntrySuffixes': set(),
        'preferPathTokens': set(),
        'suppressPathTokens': [],
        'boostSymbolTerms': set(),
        'penalizeSymbolTerms': set(),
    }

    if keyword_set & {'skill', 'skills', 'plugin', 'plugins'} and action_terms:
        profile.update({
            'name': 'skill-runtime',
            'focusManagerTokens': {'skillmanager', 'pluginmanager'},
            'focusEntrySuffixes': {'main.ts', 'preload.ts'},
            'preferPathTokens': set(),
            'suppressPathTokens': [
                '/libs/:runtime',
                '/scripts/:setup',
            ],
            'boostSymbolTerms': exact_terms & {'download', 'install', 'remove', 'delete'},
            'penalizeSymbolTerms': {'install', 'setup'} - exact_terms,
        })
    elif 'parameter-selection' in query_intent.get('labels', []):
        profile.update({
            'name': 'parameter-selection',
            'focusManagerTokens': set(),
            'focusEntrySuffixes': {'main.ts', 'preload.ts'},
            'preferPathTokens': {'/pages/', '/components/', 'display', 'settings', 'encoding', 'screen'},
            'suppressPathTokens': [],
            'boostSymbolTerms': keyword_set & (
                PARAMETER_SELECTION_TERMS | {'select', 'change', 'option', 'preset'}
            ),
            'penalizeSymbolTerms': set(),
        })

    return profile


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
    if len(parts) >= 4 and parts[0] == 'src' and parts[1] in {'main', 'renderer', 'common'}:
        return f'{parts[0]}/{parts[1]}/{parts[2]}/'
    if len(parts) >= 2 and parts[0] == 'src':
        return f'{parts[0]}/{parts[1]}/'
    if len(parts) >= 2 and parts[0] in {'SKILLs', 'skills', 'packages', 'apps', 'openclaw-extensions'}:
        return f'{parts[0]}/{parts[1]}/'
    if len(parts) == 1:
        return './'
    first_part = next(iter(parts), '')
    return './' if not first_part else f'{first_part}/'


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
    labels = set(query_intent.get('labels', []))
    sections = ['summary', 'core-files', 'code-anchors']

    if {'integration-flow', 'routing-flow', 'runtime-flow'} & labels:
        sections.append('call-chain')
    if 'configuration' in labels or 'persistence-flow' in labels:
        sections.append('config-and-persistence')
    if 'type-definition' in labels:
        sections.append('related-types')
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
    labels = set(query_intent.get('labels', []))
    query_terms = set(query_intent.get('keywords', []))
    exact_terms = set(query_intent.get('terms', []))
    action_terms = query_terms & GENERAL_QUERY_ACTION_TERMS
    exact_action_terms = exact_terms & GENERAL_QUERY_ACTION_TERMS
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
        score = 0
        structural_tokens = [
            'manager',
            'handler',
            'controller',
            'service',
            'store',
            'repository',
            'adapter',
            'gateway',
            'connector',
            'middleware',
            'transport',
            'channel',
            'session',
            'route',
            'router',
            'dispatch',
            'delivery',
        ]
        module_tokens = [
            '/main/',
            '/server/',
            '/api/',
            '/services/',
            '/handlers/',
            '/controllers/',
            '/routes/',
            '/stores/',
            '/modules/',
            '/runtime/',
        ]

        if path in snippet_paths:
            score += 40

        if lowered.startswith('src/') or lowered.startswith('app/') or lowered.startswith('server/'):
            score += 12
        if query_terms and any(token in lowered for token in ['/docs/', 'readme', 'skill.md', 'prompt', '/rules/']):
            score -= 18
        if (lowered.startswith('scripts/') or '/scripts/' in lowered) and not (query_terms & {'script', 'setup', 'build', 'cli'}):
            score -= 10

        keyword_overlap = len(path_terms & query_terms)
        if keyword_overlap:
            score += min(keyword_overlap, 3) * 12
        exact_overlap = len(path_terms & exact_terms)
        if exact_overlap:
            score += min(exact_overlap, 2) * 18

        if 'integration-flow' in labels or 'routing-flow' in labels:
            if any(token in lowered for token in structural_tokens):
                score += 28
            if any(token in lowered for token in module_tokens):
                score += 18
            if any(token in lowered for token in ['constants', '/i18n.', '/locales/', '/assets/']):
                score -= 12

        if 'configuration' in labels or 'documentation-link' in labels:
            if any(token in lowered for token in ['imsettings', 'settings.tsx', '/components/', 'schemaform', 'config', '/types/']):
                score += 25

        if 'runtime-flow' in labels:
            if any(token in lowered for token in ['runtime', 'manager', 'adapter', 'engine', 'gateway', 'connector', 'plugin']):
                score += 20
            if query_terms & GENERAL_QUERY_ACTION_TERMS and any(
                token in lowered for token in ['manager', 'service', 'handler', 'controller', 'route', 'router', 'store', 'gateway', 'adapter']
            ):
                score += 14
            if exact_action_terms and any(token in lowered for token in ['manager', 'skillmanager', 'pluginmanager']):
                score += 18

        score += score_path_with_profile(path, query_intent, read_profile)

        return (-score, 0 if path in snippet_paths else 1, path)

    return sorted(deduped, key=score_path)


def score_path_with_profile(path: str, query_intent: dict, read_profile: dict) -> int:
    lowered = normalize_rel_path(path).lower()
    query_terms = set(query_intent.get('keywords', []))
    exact_terms = set(query_intent.get('terms', []))
    action_terms = query_terms & GENERAL_QUERY_ACTION_TERMS
    exact_action_terms = exact_terms & GENERAL_QUERY_ACTION_TERMS
    score = 0

    for token in read_profile.get('focusManagerTokens', set()):
        if token in lowered:
            score += 42

    for token in read_profile.get('preferPathTokens', set()):
        if token in lowered:
            score += 26

    for suffix in read_profile.get('focusEntrySuffixes', set()):
        if lowered.endswith('/' + suffix) or lowered.endswith(suffix):
            score += 20 if suffix == 'main.ts' else 18

    if is_suppressed_by_profile(path, query_intent, read_profile):
        if '/libs/' in lowered:
            score -= 16
        if lowered.startswith('scripts/') or '/scripts/' in lowered:
            score -= 24

    if action_terms and not exact_action_terms and any(token in lowered for token in ['install', 'setup']):
        score -= 8

    return score


def is_suppressed_by_profile(path: str, query_intent: dict, read_profile: dict) -> bool:
    lowered = normalize_rel_path(path).lower()
    keyword_set = set(query_intent.get('keywords', []))
    exact_terms = set(query_intent.get('terms', []))
    if exact_terms & {'runtime', 'script', 'setup', 'python'}:
        return False
    if keyword_set & {'runtime', 'script', 'setup', 'python'} and exact_terms:
        return False
    for rule in read_profile.get('suppressPathTokens', []):
        prefix, _, token = rule.partition(':')
        prefix = prefix or ''
        token = token or ''
        if prefix and prefix not in lowered:
            continue
        if token and token not in lowered:
            continue
        return True
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

    if read_profile.get('name') == 'generic':
        return deduped

    preferred = []
    used = set()

    def add_path(path: str) -> None:
        normalized = normalize_rel_path(path)
        if not normalized or normalized in used or normalized not in seen:
            return
        used.add(normalized)
        preferred.append(normalized)

    for path in deduped:
        lowered = path.lower()
        if any(token in lowered for token in read_profile.get('preferPathTokens', set())):
            add_path(path)

    for path in deduped:
        lowered = path.lower()
        if any(token in lowered for token in read_profile.get('focusManagerTokens', set())):
            add_path(path)

    for path in snapshot.get('summary', {}).get('entryPoints', []):
        lowered = normalize_rel_path(path).lower()
        if any(lowered.endswith(suffix) for suffix in read_profile.get('focusEntrySuffixes', set())):
            add_path(path)

    for path in deduped:
        lowered = path.lower()
        if any(lowered.endswith(suffix) for suffix in read_profile.get('focusEntrySuffixes', set())):
            add_path(path)

    remainder = [
        path for path in deduped
        if path not in used and not is_suppressed_by_profile(path, query_intent, read_profile)
    ]
    return preferred + remainder


def infer_query_intent(query: str | None) -> dict:
    if not query:
        return {
            'labels': ['general-read'],
            'keywords': [],
        }

    lowered = query.lower()
    labels = []

    if any(token in lowered for token in ['config', 'setting', '配置', '参数']):
        labels.append('configuration')
    if any(token in lowered for token in ['link', 'url', 'guide', 'doc', '文档', '链接']):
        labels.append('documentation-link')
    if any(token in lowered for token in ['persist', 'save', 'store', '保存', '持久化']):
        labels.append('persistence-flow')
    if any(token in lowered for token in ['type', 'schema', 'interface', 'model', '类型']):
        labels.append('type-definition')
    if any(token in lowered for token in ['ui', 'component', 'page', '界面', '组件']):
        labels.append('ui-entry')
    if any(token in lowered for token in ['runtime', 'lifecycle', 'flow', '执行', '链路']):
        labels.append('runtime-flow')

    if not labels:
        labels.append('general-read')

    keywords = sorted({
        token
        for token in re.findall(r'[\w\-/.:#@]+', lowered)
        if len(token) >= 3
    })[:16]

    return {
        'labels': labels,
        'keywords': keywords,
    }


def infer_query_intent_v2(query: str | None) -> dict:
    if not query:
        return {
            'labels': ['general-read'],
            'keywords': [],
        }

    lowered = (normalize_query_text(query) or query).lower()
    labels = []

    if any(token in lowered for token in ['config', 'setting', '配置', '参数']):
        labels.append('configuration')
    if any(token in lowered for token in ['link', 'url', 'guide', 'doc', '文档', '链接']):
        labels.append('documentation-link')
    if any(token in lowered for token in ['persist', 'save', 'store', '保存', '持久']):
        labels.append('persistence-flow')
    if any(token in lowered for token in ['type', 'schema', 'interface', 'model', '类型']):
        labels.append('type-definition')
    if any(token in lowered for token in ['ui', 'component', 'page', '界面', '组件']):
        labels.append('ui-entry')
    if any(token in lowered for token in ['runtime', 'lifecycle', 'flow', '执行', '链路']):
        labels.append('runtime-flow')
    if any(token in lowered for token in ['gateway', 'delivery', 'route', 'handler', 'session', 'router', '投递', '路由', '网关']):
        labels.append('integration-flow')
    if any(token in lowered for token in ['delivery route', 'message', 'session', '投递', '消息', '路由', 'route']):
        labels.append('routing-flow')

    if not labels:
        labels.append('general-read')

    keywords = sorted({
        token
        for token in re.findall(r'[\w\-/.:#@]+', lowered)
        if len(token) >= 3 and '�' not in token
    })[:16]

    return {
        'labels': sorted(dict.fromkeys(labels)),
        'keywords': keywords,
    }


infer_query_intent = infer_query_intent_v2


def infer_query_intent_generic(query: str | None) -> dict:
    if not query:
        return {
            'labels': ['general-read'],
            'keywords': [],
        }

    lowered = (normalize_query_text(query) or query).lower()
    labels = []

    if any(token in lowered for token in ['config', 'setting', '配置', '参数']):
        labels.append('configuration')
    if any(token in lowered for token in ['link', 'url', 'guide', 'doc', '文档', '链接', '说明']):
        labels.append('documentation-link')
    if any(token in lowered for token in ['persist', 'save', 'store', '保存', '持久', '存储']):
        labels.append('persistence-flow')
    if any(token in lowered for token in ['type', 'schema', 'interface', 'model', '类型', '模型', '接口']):
        labels.append('type-definition')
    if any(token in lowered for token in ['ui', 'component', 'page', '界面', '组件', '页面']):
        labels.append('ui-entry')
    if any(token in lowered for token in ['runtime', 'lifecycle', 'flow', '执行', '链路', '流程']):
        labels.append('runtime-flow')
    if any(token in lowered for token in ['gateway', 'adapter', 'connector', 'integration', 'plugin', 'handler', 'manager', 'session', '网关', '适配', '连接', '集成', '插件']):
        labels.append('integration-flow')
    if any(token in lowered for token in ['route', 'router', 'delivery', 'dispatch', 'message', 'reply', 'channel', 'session', '路由', '投递', '分发', '消息', '回复', '通道', '会话']):
        labels.append('routing-flow')

    if not labels:
        labels.append('general-read')

    keywords = sorted({
        token
        for token in re.findall(r'[\w\-/.:#@\u4e00-\u9fff]+', lowered)
        if len(token) >= 2 and '锟' not in token
    })[:16]

    return {
        'labels': sorted(dict.fromkeys(labels)),
        'keywords': keywords,
    }


infer_query_intent = infer_query_intent_generic
infer_query_intent_v2 = infer_query_intent_generic


def infer_query_intent_framework(query: str | None) -> dict:
    if not query:
        return {
            'labels': ['general-read'],
            'keywords': [],
            'terms': [],
        }

    lowered = (normalize_query_text(query) or query).lower()
    terms = extract_query_terms(lowered)
    keywords = expand_query_terms(terms)
    keyword_set = set(keywords)
    labels = []

    if keyword_set & {'config', 'setting', 'configure', 'options', '配置'}:
        labels.append('configuration')
    if keyword_set & {'link', 'url', 'guide', 'doc', 'docs', 'documentation', '说明', '文档'}:
        labels.append('documentation-link')
    if keyword_set & {'persist', 'save', 'store', 'sqlite', 'db', '持久化', '存储', '保存'}:
        labels.append('persistence-flow')
    if keyword_set & {'type', 'types', 'interface', 'schema', 'model', '类型'}:
        labels.append('type-definition')
    if keyword_set & ({'ui', 'component', 'page', 'view', '界面', '组件'} | UI_SELECTION_TERMS | {'display', 'screen'}):
        labels.append('ui-entry')
    if keyword_set & PARAMETER_SELECTION_TERMS:
        labels.append('parameter-selection')
    if keyword_set & {'runtime', 'lifecycle', 'flow', 'process', 'pipeline', '运行时', '生命周期', '流程'}:
        labels.append('runtime-flow')
    if keyword_set & {'skill', 'skills', 'plugin', 'plugins'} and keyword_set & GENERAL_QUERY_ACTION_TERMS:
        labels.append('runtime-flow')
    if keyword_set & {'gateway', 'adapter', 'connector', 'integration', 'plugin', 'handler', 'manager', 'session', 'channel', '网关', '适配', '集成', '插件'}:
        labels.append('integration-flow')
    if keyword_set & {'route', 'routing', 'router', 'delivery', 'dispatch', 'message', 'reply', 'channel', 'session', '路由', '投递', '分发', '消息', '回复', '会话'}:
        labels.append('routing-flow')

    if not labels:
        labels.append('general-read')

    return {
        'labels': sorted(dict.fromkeys(labels)),
        'keywords': keywords[:20],
        'terms': terms[:20],
    }


infer_query_intent = infer_query_intent_framework
infer_query_intent_v2 = infer_query_intent_framework


def rerank_read_matches(matches: list[dict], query_intent: dict, read_profile: dict | None = None) -> list[dict]:
    read_profile = read_profile or select_read_profile(query_intent)
    labels = set(query_intent.get('labels', []))
    query_terms = set(query_intent.get('keywords', []))
    exact_terms = set(query_intent.get('terms', []))
    action_terms = query_terms & GENERAL_QUERY_ACTION_TERMS
    exact_action_terms = exact_terms & GENERAL_QUERY_ACTION_TERMS
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

        if path.startswith('src/') or path.startswith('app/') or path.startswith('server/'):
            bonus += 12
        if query_terms and any(token in path for token in ['/docs/', 'readme', 'skill.md', 'prompt', '/rules/']):
            bonus -= 18
        if (path.startswith('scripts/') or '/scripts/' in path) and not (query_terms & {'script', 'setup', 'build', 'cli'}):
            bonus -= 10

        if 'documentation-link' in labels:
            if kind == 'link':
                bonus += 40
            if any(token in haystack for token in ['guideurl', 'http://', 'https://', 'guide', 'docs', 'link']):
                bonus += 24

        if 'configuration' in labels:
            if kind in {'config-flow', 'config-type'}:
                bonus += 28
            if any(token in haystack for token in ['config', 'setting', 'persistconfig', 'updateconfig']):
                bonus += 18

        if 'ui-entry' in labels:
            if any(token in path for token in ['/components/', 'settings.tsx', 'imsettings']):
                bonus += 24

        if 'persistence-flow' in labels and any(token in haystack for token in ['persist', 'store', 'save']):
            bonus += 20

        if 'type-definition' in labels and any(token in path for token in ['/types/', '.d.ts', 'schema', 'model']):
            bonus += 16

        if 'runtime-flow' in labels:
            if any(token in path for token in ['runtime', 'adapter', 'manager', '/main/', 'gateway', 'engine', 'plugin', 'connector']):
                bonus += 28
            if any(token in haystack for token in ['runtime', 'lifecycle', 'session', 'manager', 'adapter', 'gateway', 'engine', 'plugin']):
                bonus += 20

        if 'integration-flow' in labels:
            if any(token in path for token in ['manager', 'handler', 'adapter', 'gateway', 'connector', 'plugin', 'service', '/main/', '/server/', '/api/']):
                bonus += 28
            if any(token in haystack for token in ['gateway', 'adapter', 'connector', 'integration', 'session', 'handler', 'channel', 'plugin', 'transport']):
                bonus += 22

        if 'routing-flow' in labels:
            if any(token in path for token in ['route', 'router', 'dispatch', 'delivery', 'handler', 'gateway', 'channel', 'session']):
                bonus += 24
            if any(token in haystack for token in ['route', 'delivery', 'dispatch', 'session', 'message', 'reply', 'channel', 'send', 'receive']):
                bonus += 18

        keyword_overlap = len(haystack_terms & query_terms)
        if keyword_overlap:
            bonus += min(keyword_overlap, 4) * 6
        exact_overlap = len(haystack_terms & exact_terms)
        if exact_overlap:
            bonus += min(exact_overlap, 3) * 12
        exact_symbol_overlap = len(symbol_terms & exact_terms)
        if exact_symbol_overlap:
            bonus += min(exact_symbol_overlap, 2) * 18

        if action_terms and haystack_terms & action_terms:
            bonus += 14
        if exact_action_terms and haystack_terms & exact_action_terms:
            bonus += 18
        if exact_action_terms and symbol_terms & exact_action_terms:
            bonus += 20

        bonus += score_match_with_profile(path, symbol_terms, query_intent, read_profile)

        reranked.append((item.get('score', 0) + bonus, item))

    reranked.sort(key=lambda pair: (-pair[0], pair[1].get('path') or '', pair[1].get('startLine') or 0))
    return [item for _, item in reranked]


def score_match_with_profile(path: str, symbol_terms: set[str], query_intent: dict, read_profile: dict) -> int:
    lowered = normalize_rel_path(path).lower()
    exact_terms = set(query_intent.get('terms', []))
    bonus = 0

    for token in read_profile.get('focusManagerTokens', set()):
        if token in lowered:
            bonus += 32

    for token in read_profile.get('preferPathTokens', set()):
        if token in lowered:
            bonus += 22

    for suffix in read_profile.get('focusEntrySuffixes', set()):
        if lowered.endswith('/' + suffix) or lowered.endswith(suffix):
            bonus += 16

    if is_suppressed_by_profile(path, query_intent, read_profile):
        if '/libs/' in lowered:
            bonus -= 18
        if lowered.startswith('scripts/') or '/scripts/' in lowered:
            bonus -= 24

    boosted_terms = read_profile.get('boostSymbolTerms', set())
    if boosted_terms and symbol_terms & boosted_terms:
        bonus += 24

    penalized_terms = read_profile.get('penalizeSymbolTerms', set())
    if penalized_terms and symbol_terms & penalized_terms and not (symbol_terms & boosted_terms):
        bonus -= 10

    if 'download' in exact_terms and 'download' in symbol_terms:
        bonus += 24

    return bonus


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

    if lowered.endswith(('main.ts', 'app.tsx', 'preload.ts', 'index.html')):
        return 'Entry point'
    if any(token in lowered for token in ['/components/', '.tsx', 'view', 'screen', 'page', 'settings']):
        return 'UI component'
    if any(token in lowered for token in ['/types/', '.d.ts', 'schema', 'model', 'types.ts', 'types.py']):
        return 'Type definition'
    if any(token in lowered for token in ['config', 'setting']):
        return 'Configuration'
    if any(token in lowered for token in ['manager', 'runtime', 'adapter', 'gateway', 'connector', 'agentengine', 'plugin']):
        return 'Runtime / integration'
    if any(token in lowered for token in ['route', 'router', 'dispatch', 'delivery', 'transport']):
        return 'Routing / transport'
    if any(token in lowered for token in ['handler', 'controller', 'middleware']):
        return 'Handler / controller'
    if any(token in lowered for token in ['store', 'sqlite']):
        return 'Store'
    if '/services/' in lowered or lowered.endswith('service.ts'):
        return 'Service'
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

    if any(token in lowered for token in ['skillmanager', 'runtime', 'adapter', 'gateway']):
        reasons.append('participates in runtime or skill execution flow')
    elif any(token in lowered for token in ['/components/', 'settings.tsx', 'imsettings']):
        reasons.append('entry point for user-facing configuration flow')
    elif any(token in lowered for token in ['/types/', '.d.ts', 'types.ts', 'types.py']):
        reasons.append('defines shared types consumed across modules')

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
    labels = set(query_intent.get('labels', []))
    if not labels.intersection({'integration-flow', 'routing-flow', 'runtime-flow'}):
        return []

    anchors = []
    seen = set()
    query_terms = set(query_intent.get('keywords', []))
    action_terms = query_terms & GENERAL_QUERY_ACTION_TERMS

    def allow_path(path: str) -> bool:
        lowered = (path or '').lower()
        if {'integration-flow', 'routing-flow'} & labels:
            return any(token in lowered for token in ['gateway', 'route', 'router', 'handler', 'manager', 'store', 'service', 'adapter', 'connector', 'session', 'channel', '/main/', '/server/', '/api/'])
        return True

    def classify_anchor(path: str, kind: str, preview: str = '') -> tuple[str | None, int]:
        lowered = (path or '').lower()
        combined_terms = set(extract_text_terms(f'{path or ""} {preview or ""}'))
        if lowered.endswith('index.ts') or lowered.endswith('main.ts') or lowered.endswith('app.tsx'):
            return 'entry', 0
        if 'runtime-flow' in labels and action_terms and kind in {'function', 'action-flow'} and combined_terms & action_terms:
            return 'operation', 1
        if 'manager' in lowered:
            return 'manager', 2
        if 'deliveryroute' in lowered or 'route' in lowered or 'router' in lowered or 'dispatch' in lowered:
            return 'routing', 3
        if 'handler' in lowered:
            return 'handler', 4
        if 'store' in lowered:
            return 'store', 5
        if any(token in lowered for token in ['gateway', 'adapter', 'connector', 'plugin', 'transport']):
            return 'integration', 6
        if 'type' in lowered or '.d.ts' in lowered or 'schema' in lowered or 'model' in lowered:
            return 'types', 7
        if kind == 'function':
            return 'implementation', 8
        return None, 99

    for item in snippet_items:
        path = item.get('path')
        if not path or not allow_path(path):
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
        if not allow_path(path):
            continue
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
    intent_labels = set(query_intent.get('labels', []))
    query_terms = set(query_intent.get('keywords', []))

    def path_module(path: str) -> str:
        normalized = normalize_rel_path(path)
        parts = Path(normalized).parts
        if not parts:
            return './'
        if len(parts) >= 4 and parts[0] == 'src' and parts[1] in {'main', 'renderer', 'common'}:
            return f'{parts[0]}/{parts[1]}/{parts[2]}/'
        if len(parts) >= 2 and parts[0] == 'src':
            return f'{parts[0]}/{parts[1]}/'
        if len(parts) >= 2 and parts[0] in {'SKILLs', 'skills', 'packages', 'apps', 'openclaw-extensions'}:
            return f'{parts[0]}/{parts[1]}/'
        if len(parts) == 1:
            return './'
        first_part = next(iter(parts), '')
        return './' if not first_part else f'{first_part}/'

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

    if 'configuration' in intent_labels or 'documentation-link' in intent_labels:
        for item in important_files:
            path = item['path'].lower()
            if any(token in path for token in ['config', 'setting', 'readme', 'guide', 'doc']):
                add_hop(item['path'], 'configuration or guide follow-up')
                if len(next_hops) >= 8:
                    break

    if 'type-definition' in intent_labels or 'configuration' in intent_labels:
        for item in important_files:
            path = item['path'].lower()
            if any(token in path for token in ['types', 'type', '.d.ts', 'schema', 'model']):
                add_hop(item['path'], 'type definition follow-up')
                if len(next_hops) >= 8:
                    break

    if 'persistence-flow' in intent_labels:
        for item in important_files:
            path = item['path'].lower()
            if any(token in path for token in ['store', 'service', 'sqlite', 'persist']):
                add_hop(item['path'], 'persistence flow follow-up')
                if len(next_hops) >= 8:
                    break

    if 'ui-entry' in intent_labels:
        for item in important_files:
            path = item['path'].lower()
            if any(token in path for token in ['component', 'app.tsx', 'page', 'view', 'settings']):
                add_hop(item['path'], 'ui entry follow-up')
                if len(next_hops) >= 8:
                    break

    if 'integration-flow' in intent_labels or 'routing-flow' in intent_labels:
        flow_candidates = []
        flow_candidates.extend(file_paths)
        flow_candidates.extend(item.get('path') for item in snippet_items if item.get('path'))
        flow_candidates.extend(item['path'] for item in important_files)
        deduped_candidates = []
        seen_candidates = set()
        for path in flow_candidates:
            path = normalize_rel_path(path) if path else path
            if not path or path in seen_candidates:
                continue
            seen_candidates.add(path)
            deduped_candidates.append(path)
        deduped_candidates.sort(
            key=lambda candidate: (
                -len(set(extract_text_terms(candidate)) & query_terms),
                candidate,
            )
        )
        for path in deduped_candidates:
            lowered = (path or '').lower()
            if any(token in lowered for token in ['gateway', 'adapter', 'connector', 'manager', 'handler', 'route', 'router', 'dispatch', 'delivery', 'store', 'service', 'session', 'channel']):
                add_hop(path, 'integration or routing follow-up')
                if len(next_hops) >= 8:
                    break

    if 'runtime-flow' in intent_labels:
        runtime_candidates = []
        matched_modules = {path_module(path) for path in matched_paths + file_paths if path}
        for module_name in matched_modules:
            runtime_candidates.extend(module_file_map.get(module_name, [])[:8])
        runtime_candidates.extend(snapshot.get('summary', {}).get('entryPoints', [])[:8])
        runtime_candidates.extend(item['path'] for item in important_files)
        deduped_runtime_candidates = []
        seen_runtime = set()
        for path in runtime_candidates:
            path = normalize_rel_path(path) if path else path
            if not path or path in seen_runtime:
                continue
            seen_runtime.add(path)
            deduped_runtime_candidates.append(path)
        deduped_runtime_candidates.sort(
            key=lambda candidate: (
                -len(set(extract_text_terms(candidate)) & query_terms),
                candidate,
            )
        )
        for path in deduped_runtime_candidates:
            lowered = path.lower()
            if any(token in lowered for token in ['main.ts', 'preload', 'skillmanager', 'runtime', 'adapter', 'gateway', 'engine', '/main/', 'channel', 'session', 'sync']):
                add_hop(path, 'runtime flow follow-up')
                if len(next_hops) >= 8:
                    break

    if query_terms:
        for item in important_files:
            lowered = item['path'].lower()
            if any(keyword in lowered for keyword in query_terms):
                add_hop(item['path'], 'keyword-related important file')
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
            if dir_name in EXCLUDE_DIRS or dir_name.startswith('.'):
                continue
            rel_dir = dir_name if not rel_root else f'{rel_root}/{dir_name}'
            if is_excluded_path(rel_dir):
                continue
            filtered_dirs.append(dir_name)
        dirs[:] = filtered_dirs

        for filename in filenames:
            if filename.startswith('.'):
                continue
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
    output_file = output_dir / 'miloya-codebase.json'
    index_state_file = output_dir / 'miloya-codebase.index.json'

    # Scan files
    files = scan_files(project_path)
    source_fingerprint = build_source_fingerprint(files, project_path)
    current_signatures = build_file_signatures(files, project_path)
    newest_source_mtime = get_newest_source_mtime(files)
    existing_snapshot = load_existing_snapshot(output_file)
    existing_index_state = load_existing_index_state(index_state_file)

    if (
        existing_snapshot
        and not force
        and existing_snapshot.get('version') == SNAPSHOT_VERSION
        and existing_snapshot.get('sourceFingerprint') == source_fingerprint
    ):
        freshness = existing_snapshot.setdefault('freshness', {})
        freshness['stale'] = False
        freshness['reason'] = 'source fingerprint unchanged'
        freshness['newestSourceMtime'] = newest_source_mtime
        existing_snapshot['index'] = build_index_metadata(
            base,
            index_state_file,
            existing_index_state,
            current_signatures,
            (existing_index_state or {}).get('chunks', []),
            reusing_snapshot=True,
        )
        existing_snapshot['chunkCatalog'] = build_chunk_catalog(
            (existing_index_state or {}).get('chunks', []),
            existing_snapshot.get('importantFiles', []),
        )
        return existing_snapshot

    file_records, total_lines = collect_file_records(files, project_path)
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
    retrieval, context_packs = build_retrieval_artifacts(chunks, important_files, graph, external_context)

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
        'architecture': architecture
    }

    # Save to file
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
    save_index_state(index_state_file, current_signatures, chunks, file_records, source_fingerprint)

    print(f"Snapshot saved to: {output_file}", file=sys.stderr)
    return snapshot


def read_query_input(
    inline_query: str | None = None,
    escaped_query: str | None = None,
    query_file: str | None = None,
    use_stdin: bool = False,
) -> str | None:
    if escaped_query:
        return codecs.decode(escaped_query, 'unicode_escape').strip() or None

    if query_file:
        query_path = Path(query_file)
        if not query_path.exists():
            raise FileNotFoundError(f'Query file not found: {query_file}')
        return query_path.read_text(encoding='utf-8-sig').strip() or None

    if use_stdin:
        return sys.stdin.read().strip() or None

    return inline_query


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python generate.py <project_path> [read|--read|report|--report] [--force] "
            "[--task <task>] [--query <query> | --query-escaped <ascii_escaped_query> "
            "| --query-file <utf8_file> | --query-stdin]",
            file=sys.stderr,
        )
        sys.exit(1)

    project_path = sys.argv[1]
    cli_args = sys.argv[2:]
    read_mode = '--read' in cli_args or (len(cli_args) > 0 and cli_args[0] == 'read')
    report_mode = '--report' in cli_args or (len(cli_args) > 0 and cli_args[0] == 'report')
    force = '--force' in cli_args or '--refresh' in cli_args or (len(cli_args) > 0 and cli_args[0] == 'refresh')
    task = 'understand-project'
    query = None
    escaped_query = None
    query_file = None
    query_stdin = '--query-stdin' in cli_args

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

    if report_mode:
        base = Path(project_path)
        snapshot = load_existing_snapshot(base / 'repo' / 'progress' / 'miloya-codebase.json')
        if not snapshot or force:
            snapshot = generate_snapshot(project_path, force)

        index_state = load_existing_index_state(base / 'repo' / 'progress' / 'miloya-codebase.index.json')
        write_json_stdout(build_report_payload(snapshot, index_state, task, query))
        return

    if read_mode:
        base = Path(project_path)
        snapshot = load_existing_snapshot(base / 'repo' / 'progress' / 'miloya-codebase.json')
        if not snapshot:
            print(
                "Error: snapshot not found. Run /miloya-codebase or /miloya-codebase refresh first.",
                file=sys.stderr,
            )
            sys.exit(1)

        index_state = load_existing_index_state(base / 'repo' / 'progress' / 'miloya-codebase.index.json')
        write_json_stdout(build_read_payload(snapshot, index_state, task, query))
        return

    snapshot = generate_snapshot(project_path, force)

    if query:
        index_state = load_existing_index_state(Path(project_path) / 'repo' / 'progress' / 'miloya-codebase.index.json')
        focus_pack = build_focus_context_pack(query, task, snapshot, index_state)
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
