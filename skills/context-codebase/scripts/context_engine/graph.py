from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path


LOCAL_CODE_EXTENSIONS = ['.ts', '.tsx', '.js', '.jsx', '.py']


def build_code_graph(
    file_records: list[dict],
    unique_routes: list[dict],
    unique_models: list[dict],
    key_functions: list[dict],
    workspace: dict,
    project_root: Path | None = None,
) -> dict:
    file_paths = {record['path'] for record in file_records}
    path_to_record = {record['path']: record for record in file_records}
    resolution_config = load_resolution_config(project_root)
    file_dependencies = {}
    dependency_edges = []
    module_edge_counts = Counter()
    symbol_index = []

    for record in file_records:
        resolved_dependencies = resolve_local_dependencies(record, file_paths, resolution_config)
        file_dependencies[record['path']] = resolved_dependencies
        source_module = module_for_path(record['path'])

        for target_path in resolved_dependencies:
            dependency_edges.append({
                'source': record['path'],
                'target': target_path,
                'type': 'imports',
            })
            target_module = module_for_path(target_path)
            if source_module != target_module:
                module_edge_counts[(source_module, target_module)] += 1

        for route in record.get('apiRoutes', []):
            symbol_index.append({
                'kind': 'route',
                'name': f'{route.get("method", "GET")} {route.get("path", "")}',
                'file': record['path'],
                'line': route.get('line'),
                'confidence': record.get('analysisConfidence', 'none'),
            })

        for model in record.get('dataModels', []):
            symbol_index.append({
                'kind': 'model',
                'name': model['name'],
                'file': record['path'],
                'line': model.get('line'),
                'type': model.get('type'),
                'confidence': record.get('analysisConfidence', 'none'),
            })

        for func in record.get('keyFunctions', []):
            symbol_index.append({
                'kind': 'function',
                'name': func['name'],
                'file': record['path'],
                'line': func['line'],
                'confidence': record.get('analysisConfidence', 'none'),
            })

    inbound_counts = Counter()
    outbound_counts = Counter()
    for edge in dependency_edges:
        outbound_counts[edge['source']] += 1
        inbound_counts[edge['target']] += 1

    hotspots = []
    for record in file_records:
        path = record['path']
        hotspots.append({
            'path': path,
            'language': record['language'],
            'inbound': inbound_counts[path],
            'outbound': outbound_counts[path],
            'signals': len(record.get('apiRoutes', [])) + len(record.get('dataModels', [])) + len(record.get('keyFunctions', [])),
        })

    hotspots.sort(key=lambda item: (-item['inbound'], -item['signals'], item['path']))

    route_to_handler = [
        {
            'method': route['method'],
            'path': route['path'],
            'handler': route['handler'],
        }
        for route in unique_routes
    ]

    packages = []
    for package in workspace.get('packages', []):
        packages.append({
            'name': package['name'],
            'path': package['path'],
            'role': package['role'],
            'entryPoints': package['entryPoints'],
            'fileCount': package['fileCount'],
        })

    return {
        'stats': {
            'files': len(file_records),
            'symbols': len(symbol_index),
            'dependencyEdges': len(dependency_edges),
            'routeCount': len(unique_routes),
            'modelCount': len(unique_models),
            'functionCount': len(key_functions),
        },
        'packages': packages,
        'moduleDependencies': [
            {'source': source, 'target': target, 'count': count}
            for (source, target), count in sorted(module_edge_counts.items(), key=lambda item: (-item[1], item[0][0], item[0][1]))
        ][:80],
        'fileDependencies': [
            {'path': path, 'dependsOn': targets}
            for path, targets in sorted(file_dependencies.items())
            if targets
        ][:120],
        'routeToHandler': route_to_handler[:120],
        'symbolIndex': sorted(symbol_index, key=lambda item: (item['file'], item.get('line') or 0, item['kind'], item['name']))[:240],
        'hotspots': hotspots[:30],
        'pathIndex': build_path_index(path_to_record),
    }


def build_path_index(path_to_record: dict[str, dict]) -> list[dict]:
    module_to_paths = defaultdict(list)
    for path, record in path_to_record.items():
        module_to_paths[module_for_path(path)].append({
            'path': path,
            'language': record.get('language'),
            'lineCount': record.get('lineCount'),
        })

    return [
        {
            'module': module,
            'files': sorted(items, key=lambda item: item['path'])[:40],
        }
        for module, items in sorted(module_to_paths.items())
    ]


def module_for_path(path: str) -> str:
    parts = Path(path).parts
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


def resolve_local_dependencies(record: dict, file_paths: set[str], resolution_config: dict | None = None) -> list[str]:
    resolved = []
    current_path = Path(record['path'])
    language = record.get('language')
    resolution_config = resolution_config or {}

    for import_path in record.get('imports', []):
        candidate_paths = []

        if language in {'TypeScript', 'JavaScript'}:
            candidate_paths.extend(resolve_js_ts_candidates(current_path, import_path, resolution_config))
        elif language == 'Python':
            if import_path.startswith('.'):
                trimmed = import_path.lstrip('.')
                if trimmed:
                    base_path = normalize_posix_path(current_path.parent.joinpath(trimmed.replace('.', '/')))
                    candidate_paths.extend(expand_code_candidates(base_path))
            else:
                base_path = import_path.replace('.', '/')
                candidate_paths.extend(expand_code_candidates(base_path))
                if '/' in record['path']:
                    local_base = normalize_posix_path(Path(record['path']).parent.joinpath(import_path.replace('.', '/')))
                    candidate_paths.extend(expand_code_candidates(local_base))

        for candidate in candidate_paths:
            if candidate in file_paths and candidate != record['path']:
                resolved.append(candidate)
                break

    return sorted(dict.fromkeys(resolved))


def expand_code_candidates(base_path: str) -> list[str]:
    candidates = [base_path]
    for ext in LOCAL_CODE_EXTENSIONS:
        candidates.append(f'{base_path}{ext}')
        candidates.append(f'{base_path}/index{ext}')
    return candidates


def normalize_posix_path(path_like: Path) -> str:
    return str(path_like).replace('\\', '/').replace('//', '/')


def resolve_js_ts_candidates(current_path: Path, import_path: str, resolution_config: dict) -> list[str]:
    candidates = []

    if import_path.startswith('.'):
        base_path = normalize_posix_path(current_path.parent.joinpath(import_path))
        return expand_code_candidates(base_path)

    alias_mappings = resolution_config.get('paths', [])
    base_url = resolution_config.get('baseUrl', '')

    for prefix, targets in alias_mappings:
        if prefix.endswith('*'):
            stem = prefix[:-1]
            if not import_path.startswith(stem):
                continue
            remainder = import_path[len(stem):]
        elif import_path == prefix:
            remainder = ''
        else:
            continue

        for target in targets:
            rewritten = target.replace('*', remainder)
            target_path = Path(base_url, rewritten) if base_url else Path(rewritten)
            candidates.extend(expand_code_candidates(normalize_posix_path(target_path)))

    if base_url:
        candidates.extend(expand_code_candidates(normalize_posix_path(Path(base_url, import_path))))

    candidates.extend(expand_code_candidates(import_path.replace('\\', '/')))
    return candidates


def load_resolution_config(project_root: Path | None) -> dict:
    if not project_root:
        return {}
    project_root = Path(project_root)

    for config_name in ('tsconfig.json', 'jsconfig.json'):
        config_path = project_root / config_name
        if not config_path.exists():
            continue

        try:
            raw = config_path.read_text(encoding='utf-8')
        except OSError:
            continue

        try:
            payload = json.loads(strip_json_comments(raw))
        except json.JSONDecodeError:
            continue

        compiler_options = payload.get('compilerOptions', {})
        base_url = compiler_options.get('baseUrl', '')
        raw_paths = compiler_options.get('paths', {})
        alias_paths = []
        if isinstance(raw_paths, dict):
            for prefix, targets in raw_paths.items():
                if not isinstance(prefix, str):
                    continue
                if isinstance(targets, str):
                    targets = [targets]
                if not isinstance(targets, list):
                    continue
                cleaned_targets = [target for target in targets if isinstance(target, str)]
                if cleaned_targets:
                    alias_paths.append((prefix, cleaned_targets))

        return {
            'baseUrl': str(Path(base_url)).replace('\\', '/').strip('./') if base_url else '',
            'paths': alias_paths,
        }

    return {}


def strip_json_comments(raw: str) -> str:
    without_block = re_sub_safe(r'/\*[\s\S]*?\*/', '', raw)
    return re_sub_safe(r'^\s*//.*$', '', without_block, multiline=True)


def re_sub_safe(pattern: str, repl: str, text: str, multiline: bool = False) -> str:
    import re

    flags = re.MULTILINE if multiline else 0
    return re.sub(pattern, repl, text, flags=flags)
