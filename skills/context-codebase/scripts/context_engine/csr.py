from __future__ import annotations

import re
from pathlib import Path
from typing import Any, TypeAlias, TypedDict, cast

from .retrieval import TASK_BLUEPRINTS, retrieve_chunks


StrList: TypeAlias = list[str]
ChunkMatch: TypeAlias = dict[str, Any]
SnapshotDict: TypeAlias = dict[str, Any]
IndexStateDict: TypeAlias = dict[str, Any]


class RouteProfile(TypedDict):
    name: str
    strategies: StrList
    route_terms: StrList
    path_hints: StrList
    preferred_kinds: set[str]


class RouteMetadata(TypedDict):
    engine: str
    task: str
    profile: str
    subfocus: str
    strategies: StrList
    routeTerms: StrList
    pathHints: StrList
    preferredKinds: StrList
    focusModules: StrList
    confidence: float


ROUTE_PROFILES: dict[str, RouteProfile] = {
    'understand-project': {
        'name': 'orientation',
        'strategies': ['task-blueprint', 'importance-boost', 'graph-expansion'],
        'route_terms': ['entry', 'architecture', 'module', 'dependency', 'overview'],
        'path_hints': ['src/', 'app/', 'server/', 'packages/', 'apps/'],
        'preferred_kinds': {'section', 'function', 'model', 'route'},
    },
    'feature-delivery': {
        'name': 'implementation-surface',
        'strategies': ['task-blueprint', 'semantic-expansion', 'dependency-walk'],
        'route_terms': ['feature', 'service', 'handler', 'flow', 'integration', 'create', 'update'],
        'path_hints': ['src/', 'app/', 'server/', '/services/', '/handlers/', '/routes/'],
        'preferred_kinds': {'function', 'route', 'action-flow', 'model'},
    },
    'bugfix-investigation': {
        'name': 'failure-trace',
        'strategies': ['task-blueprint', 'recent-change-boost', 'dependency-walk', 'execution-path'],
        'route_terms': ['error', 'failure', 'exception', 'route', 'router', 'handler', 'service', 'dispatch'],
        'path_hints': ['/routes/', '/router', '/handler', '/controller', '/service', '/runtime/'],
        'preferred_kinds': {'function', 'route', 'action-flow', 'config-flow'},
    },
    'code-review': {
        'name': 'risk-surface',
        'strategies': ['task-blueprint', 'recent-change-boost', 'hotspot-boost', 'dependency-walk'],
        'route_terms': ['risk', 'edge', 'critical', 'review', 'validation', 'config', 'test'],
        'path_hints': ['/src/', '/app/', '/server/', '/services/', '/routes/'],
        'preferred_kinds': {'function', 'route', 'model', 'config-flow'},
    },
    'onboarding': {
        'name': 'navigation',
        'strategies': ['task-blueprint', 'orientation', 'graph-expansion'],
        'route_terms': ['readme', 'architecture', 'entry', 'module', 'convention'],
        'path_hints': ['README', 'src/', 'app/', 'server/', 'packages/'],
        'preferred_kinds': {'section', 'function', 'route', 'model'},
    },
}

SUBFOCUS_PATTERNS = [
    (
        {'route', 'router', 'routing', 'dispatch', 'flow', 'path', '链路', '路由', '调用', '入口'},
        'execution-path',
        ['route', 'router', 'dispatch', 'handler', 'controller', 'service'],
    ),
    (
        {'config', 'setting', 'settings', 'env', 'schema', '配置', '环境', '变量'},
        'configuration',
        ['config', 'settings', 'env', 'schema', 'validation'],
    ),
    (
        {'type', 'types', 'schema', 'model', 'interface', 'typing', '类型', '模型', '结构'},
        'type-contract',
        ['type', 'schema', 'interface', 'model', 'payload'],
    ),
    (
        {'test', 'tests', 'spec', 'fixture', 'e2e', '用例', '测试'},
        'test-surface',
        ['test', 'spec', 'fixture', 'validation', 'regression'],
    ),
    (
        {'db', 'sql', 'query', 'cache', 'store', 'redis', '数据库', '缓存'},
        'data-surface',
        ['db', 'query', 'cache', 'store', 'repository', 'model'],
    ),
]

DOC_TOKENS = ('/docs/', 'readme', 'skill.md', '/rules/', '/references/')
STOPWORDS = {
    'the', 'and', 'for', 'with', 'from', 'that', 'this', 'what', 'where', 'which',
    'when', 'read', 'mode', 'task', 'help', 'need', 'please', 'about', 'into',
}


def build_csr_read_enhancement(
    snapshot: SnapshotDict,
    index_state: IndexStateDict | None,
    task: str,
    query: str | None,
    query_intent: SnapshotDict,
) -> SnapshotDict:
    chunks = cast(list[ChunkMatch], (index_state or {}).get('chunks', []))
    if not chunks:
        return {
            'enabled': False,
            'route': build_route_metadata(task, query_intent, [], []),
            'matches': [],
            'files': [],
            'searchScope': {'preferPaths': [], 'notes': []},
        }

    graph = cast(SnapshotDict, snapshot.get('graph', {}))
    important_files = cast(list[SnapshotDict], snapshot.get('importantFiles', []))
    external_context = cast(SnapshotDict, snapshot.get('externalContext', {}))
    retrieval = cast(SnapshotDict, snapshot.get('retrieval', {}))
    important_ranks = {
        path: index
        for index, item in enumerate(important_files)
        if (path := cast(str | None, item.get('path')))
    }
    recent_changed = set(cast(list[str], external_context.get('recentChangedFiles', [])))
    dependency_map = {
        cast(str, item['path']): cast(list[str], item.get('dependsOn', []))
        for item in cast(list[SnapshotDict], graph.get('fileDependencies', []))
        if item.get('path')
    }
    module_file_map = {
        cast(str, item.get('module')): [
            cast(str, file_item.get('path'))
            for file_item in cast(list[SnapshotDict], item.get('files', []))
            if file_item.get('path')
        ]
        for item in cast(list[SnapshotDict], graph.get('pathIndex', []))
        if item.get('module')
    }

    route = build_route_metadata(
        task,
        query_intent,
        cast(list[str], retrieval.get('availableTasks', [])),
        important_files,
    )
    query_variants = build_query_variants(task, query, query_intent, retrieval, route)
    merged_matches = collect_csr_matches(
        query_variants,
        chunks,
        important_ranks,
        recent_changed,
        dependency_map,
        task,
        query_intent,
        route,
    )
    files = collect_related_files(
        merged_matches,
        dependency_map,
        module_file_map,
        cast(list[str], cast(SnapshotDict, snapshot.get('summary', {})).get('entryPoints', [])),
    )
    search_scope = {
        'preferPaths': files[:10],
        'notes': [
            f"CSR route={route['profile']} subfocus={route['subfocus']}.",
            'Prefer CSR-ranked files before widening to repo-wide search.',
            'Follow dependency-linked files before opening unrelated modules.',
        ],
    }

    return {
        'enabled': True,
        'route': route,
        'matches': merged_matches[:18],
        'files': files[:14],
        'searchScope': search_scope,
    }


def build_route_metadata(
    task: str,
    query_intent: SnapshotDict,
    available_tasks: list[str],
    important_files: list[SnapshotDict],
) -> RouteMetadata:
    route_profile = ROUTE_PROFILES.get(task, ROUTE_PROFILES['understand-project'])
    query_terms = list(dict.fromkeys([
        *cast(list[str], query_intent.get('terms', [])),
        *cast(list[str], query_intent.get('keywords', [])),
    ]))
    subfocus, subfocus_terms = infer_subfocus(query_terms)
    focus_modules = infer_focus_modules([
        cast(str, item.get('path'))
        for item in important_files[:8]
        if item.get('path')
    ])

    confidence = 0.55
    if query_intent.get('preferredTask') == task:
        confidence += 0.2
    if subfocus != 'general':
        confidence += 0.1
    if task in available_tasks:
        confidence += 0.05

    return {
        'engine': 'csr',
        'task': task,
        'profile': route_profile['name'],
        'subfocus': subfocus,
        'strategies': route_profile['strategies'],
        'routeTerms': list(dict.fromkeys(route_profile['route_terms'] + subfocus_terms))[:10],
        'pathHints': route_profile['path_hints'],
        'preferredKinds': sorted(route_profile['preferred_kinds']),
        'focusModules': focus_modules[:6],
        'confidence': min(confidence, 0.95),
    }


def build_query_variants(
    task: str,
    query: str | None,
    query_intent: SnapshotDict,
    retrieval: SnapshotDict,
    route: RouteMetadata,
) -> list[str]:
    blueprint_query = cast(str, TASK_BLUEPRINTS.get(task, {}).get('query', ''))
    base_terms = list(dict.fromkeys([
        *cast(list[str], query_intent.get('terms', [])),
        *cast(list[str], query_intent.get('keywords', [])),
    ]))
    project_vocabulary = cast(SnapshotDict, retrieval.get('projectVocabulary', {}))
    related_terms = cast(dict[str, list[str]], project_vocabulary.get('relatedTerms', {}))
    expanded_terms = list(base_terms)

    for term in list(base_terms)[:12]:
        for related in related_terms.get(term.lower(), [])[:3]:
            if related not in expanded_terms:
                expanded_terms.append(related)

    variants = []
    if query:
        variants.append(query)
    if blueprint_query:
        variants.append(' '.join([blueprint_query, *expanded_terms[:10]]).strip())
    route_variant = ' '.join([*expanded_terms[:12], *route.get('routeTerms', [])[:8]]).strip()
    if route_variant:
        variants.append(route_variant)

    deduped = []
    seen = set()
    for variant in variants:
        normalized = normalize_text(variant)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)
    return deduped[:3]


def collect_csr_matches(
    query_variants: list[str],
    chunks: list[ChunkMatch],
    important_ranks: dict[str, int],
    recent_changed: set[str],
    dependency_map: dict[str, list[str]],
    task: str,
    query_intent: SnapshotDict,
    route: RouteMetadata,
) -> list[ChunkMatch]:
    merged: dict[str, tuple[int, ChunkMatch]] = {}

    for variant in query_variants:
        matches = retrieve_chunks(
            query=variant,
            chunks=chunks,
            important_ranks=important_ranks,
            recent_changed=recent_changed,
            file_dependency_map=dependency_map,
            task=task,
            limit=20,
        )
        for match in matches:
            score = score_csr_match(match, query_intent, route, recent_changed)
            match_id = cast(str, match['id'])
            existing = merged.get(match_id)
            if existing is None or score > existing[0]:
                enriched = dict(match)
                reasons = list(cast(list[str], match.get('reasons', [])))
                reasons.append(f"csr route={route['profile']}")
                if route.get('subfocus') != 'general':
                    reasons.append(f"csr subfocus={route['subfocus']}")
                enriched['reasons'] = list(dict.fromkeys(reasons))[:4]
                enriched['score'] = score
                merged[match_id] = (score, enriched)

    ranked = sorted(
        (item for _, item in merged.values()),
        key=lambda item: (-item.get('score', 0), item.get('path') or '', item.get('startLine') or 0),
    )
    return ranked


def score_csr_match(
    match: ChunkMatch,
    query_intent: SnapshotDict,
    route: RouteMetadata,
    recent_changed: set[str],
) -> int:
    path = (match.get('path') or '').lower()
    kind = (match.get('kind') or '').lower()
    preview = (match.get('preview') or '').lower()
    signals = ' '.join(cast(list[str], match.get('signals', []))).lower()
    haystack = ' '.join([path, kind, preview, signals])
    query_terms = set(cast(list[str], query_intent.get('keywords', [])))
    exact_terms = set(cast(list[str], query_intent.get('terms', [])))
    route_terms = set(route.get('routeTerms', []))
    path_terms = extract_terms(path)

    score = int(match.get('score', 0))
    if kind in set(route.get('preferredKinds', [])):
        score += 14
    if any(token.lower() in path for token in route.get('routeTerms', [])[:6]):
        score += 12
    if any(token.lower() in path for token in route.get('pathHints', [])):
        score += 8
    score += min(len(exact_terms & extract_terms(haystack)), 3) * 10
    score += min(len(query_terms & extract_terms(haystack)), 4) * 5
    score += min(len(route_terms & extract_terms(haystack)), 3) * 7
    score += min(len(path_terms & exact_terms), 3) * 10
    score += min(len(path_terms & query_terms), 4) * 6

    for index, hint in enumerate(cast(list[str], query_intent.get('dynamicPathHints', []))[:6]):
        normalized_hint = normalize_path(hint).lower()
        if path == normalized_hint or path.startswith(normalized_hint.rstrip('/') + '/'):
            score += max(24 - index * 4, 8)
        elif normalized_hint and normalized_hint in path:
            score += max(14 - index * 2, 4)

    if match.get('path') in recent_changed and route.get('task') in {'bugfix-investigation', 'code-review'}:
        score += 12
    if is_probably_test_path(path) and route.get('subfocus') != 'test-surface':
        score -= 28
    if any(token in path for token in DOC_TOKENS) and route.get('subfocus') not in {'general', 'configuration'}:
        score -= 18
    if path.endswith('.json') and not (path_terms & (query_terms | exact_terms)):
        score -= 10

    return score


def collect_related_files(
    matches: list[ChunkMatch],
    dependency_map: dict[str, list[str]],
    module_file_map: dict[str, list[str]],
    entry_points: list[str],
) -> list[str]:
    ordered = []
    seen = set()

    def add(path: str | None) -> None:
        normalized = normalize_path(path or '')
        if not normalized or normalized in seen:
            return
        seen.add(normalized)
        ordered.append(normalized)

    for match in matches[:10]:
        path = cast(str | None, match.get('path'))
        add(path)
        if path:
            for dependency in dependency_map.get(path, [])[:4]:
                add(dependency)

    matched_modules = {
        infer_path_module(cast(str, item.get('path', '')))
        for item in matches[:8]
    }
    for module_name in matched_modules:
        for path in module_file_map.get(module_name, [])[:4]:
            add(path)

    for path in entry_points[:4]:
        add(path)

    return ordered


def infer_subfocus(query_terms: list[str]) -> tuple[str, list[str]]:
    lowered_terms = {term.lower() for term in query_terms}
    for triggers, name, route_terms in SUBFOCUS_PATTERNS:
        if lowered_terms & triggers:
            return name, route_terms
    return 'general', []


def infer_focus_modules(paths: list[str]) -> list[str]:
    modules = []
    seen = set()
    for path in paths:
        module = infer_path_module(path or '')
        if not module or module in seen:
            continue
        seen.add(module)
        modules.append(module)
    return modules


def infer_path_module(path: str) -> str:
    normalized = normalize_path(path)
    parts = Path(normalized).parts
    if not parts:
        return './'
    if len(parts) >= 4 and parts[0] == 'src' and parts[1] in {'main', 'renderer', 'common'}:
        return f'{parts[0]}/{parts[1]}/{parts[2]}/'
    if len(parts) >= 2:
        return f'{parts[0]}/{parts[1]}/'
    return './'


def extract_terms(text: str | None) -> set[str]:
    normalized = normalize_text(text or '')
    raw_tokens = re.findall(r'[A-Za-z][A-Za-z0-9_./-]*|[\u4e00-\u9fff]+|\d+', normalized.lower())
    return {
        token
        for token in raw_tokens
        if len(token) >= 2 and token not in STOPWORDS
    }


def normalize_text(text: str) -> str:
    text = text.replace('\ufffd', ' ')
    text = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', text)
    text = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', text)
    text = re.sub(r'[^A-Za-z0-9_\s\-/.:#@\u4e00-\u9fff]+', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def normalize_path(path: str) -> str:
    return path.replace('\\', '/').strip()


def is_probably_test_path(path: str) -> bool:
    lowered = normalize_path(path).lower()
    file_name = Path(lowered).name
    return any(
        token in lowered
        for token in (
            '/tests/',
            '/__tests__/',
            '.test.',
            '.spec.',
            '.e2e.',
            '_test.',
            'test-harness',
            'test_harness',
            'fixtures/',
        )
    ) or file_name.startswith(('test_', 'spec_'))
