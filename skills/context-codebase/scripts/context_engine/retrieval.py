from __future__ import annotations

import re
from collections import Counter, defaultdict


STOPWORDS = {
    'the', 'and', 'for', 'with', 'from', 'that', 'this', 'into', 'when', 'want',
    'your', 'have', 'what', 'where', 'which', 'does', 'read', 'code', 'file',
    'files', 'repo', 'project', 'understand', 'task', 'mode', 'need', 'use',
}

CONFIG_QUERY_TOKENS = {
    'config', 'setting', 'settings', 'env', 'schema', 'workflow', 'workflows',
    'pipeline', 'pipelines', 'release', 'releases', 'ci', 'cd', 'action',
    'actions', 'manifest', 'secrets', 'secret', 'deploy', 'deployment',
}

MANIFEST_SUFFIXES = {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf'}
DOC_SUFFIXES = {'.md', '.mdx', '.rst', '.txt', '.adoc'}
DOC_NAME_TOKENS = {'readme', 'guide', 'manual', 'wiki', 'documentation', 'doc', 'skill', 'skills'}


def is_probably_test_path(path: str) -> bool:
    lowered = path.replace('\\', '/').lower()
    filename = lowered.rsplit('/', 1)[-1]
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
    ) or filename.startswith(('test_', 'spec_'))


TASK_BLUEPRINTS = {
    'understand-project': {
        'query': 'project overview architecture entry points important files modules dependencies',
        'description': 'Orient a new model to the project quickly.',
    },
    'feature-delivery': {
        'query': 'entry points routes services models integration config implementation pattern',
        'description': 'Add or extend behavior using existing project structure.',
    },
    'bugfix-investigation': {
        'query': 'recent changes error handling validation tests routes services config',
        'description': 'Trace failure paths and relevant surrounding code.',
    },
    'code-review': {
        'query': 'recent changes critical paths dependencies tests configuration edge cases',
        'description': 'Review touched areas and their immediate risk surface.',
    },
    'onboarding': {
        'query': 'readme architecture important files conventions packages modules',
        'description': 'Help a new engineer or model build a working mental map.',
    },
}


def build_retrieval_artifacts(
    chunks: list[dict],
    important_files: list[dict],
    graph: dict,
    external_context: dict,
) -> tuple[dict, dict]:
    important_ranks = {item['path']: index for index, item in enumerate(important_files)}
    recent_changed = set(external_context.get('recentChangedFiles', []))
    file_dependency_map = {
        item['path']: item['dependsOn']
        for item in graph.get('fileDependencies', [])
    }

    project_vocabulary = build_project_vocabulary(chunks)

    retrieval = {
        'defaultTask': 'understand-project',
        'availableTasks': list(TASK_BLUEPRINTS.keys()),
        'strategies': ['keyword', 'graph-expansion', 'importance-boost', 'recent-change-boost'],
        'keywordVocabularySize': estimate_vocabulary(chunks),
        'chunkCount': len(chunks),
        'projectVocabulary': project_vocabulary,
        'sampleQueries': [
            blueprint['query']
            for blueprint in TASK_BLUEPRINTS.values()
        ],
    }

    context_packs = {}
    for task, blueprint in TASK_BLUEPRINTS.items():
        context_packs[task] = build_context_pack(
            task,
            blueprint['query'],
            blueprint['description'],
            chunks,
            important_ranks,
            recent_changed,
            file_dependency_map,
        )

    return retrieval, context_packs


def build_context_pack(
    task: str,
    query: str,
    description: str,
    chunks: list[dict],
    important_ranks: dict[str, int],
    recent_changed: set[str],
    file_dependency_map: dict[str, list[str]],
) -> dict:
    ranked = retrieve_chunks(
        query,
        chunks,
        important_ranks,
        recent_changed,
        file_dependency_map,
        task=task,
        limit=10,
    )
    related_files = []
    for item in ranked:
        related_files.append(item['path'])
        related_files.extend(file_dependency_map.get(item['path'], []))

    return {
        'task': task,
        'description': description,
        'query': query,
        'chunks': ranked,
        'files': list(dict.fromkeys(related_files))[:12],
    }


def retrieve_chunks(
    query: str,
    chunks: list[dict],
    important_ranks: dict[str, int],
    recent_changed: set[str],
    file_dependency_map: dict[str, list[str]],
    task: str,
    limit: int,
) -> list[dict]:
    query_tokens = tokenize(query)
    scored = []

    for chunk in chunks:
        score, reasons = score_chunk(
            chunk,
            query_tokens,
            important_ranks,
            recent_changed,
            task,
        )
        if score <= 0:
            continue
        scored.append((score, reasons, chunk))

    scored.sort(key=lambda item: (-item[0], item[2]['path'], item[2]['startLine']))
    selected = []
    seen_ids = set()
    selected_files = set()

    for score, reasons, chunk in scored:
        if chunk['id'] in seen_ids:
            continue
        seen_ids.add(chunk['id'])
        selected_files.add(chunk['path'])
        selected.append(format_chunk_match(chunk, score, reasons))
        if len(selected) >= limit:
            break

    if task in {'bugfix-investigation', 'code-review'}:
        for chunk in chunks:
            if chunk['path'] not in recent_changed or chunk['id'] in seen_ids:
                continue
            selected.append(format_chunk_match(chunk, 10, ['recently changed file']))
            seen_ids.add(chunk['id'])
            selected_files.add(chunk['path'])
            if len(selected) >= limit:
                break

    if task in {'feature-delivery', 'bugfix-investigation'}:
        dependency_expansions = []
        for path in list(selected_files):
            for dependency in file_dependency_map.get(path, []):
                dependency_expansions.append(dependency)

        for dependency in dependency_expansions:
            for chunk in chunks:
                if chunk['path'] != dependency or chunk['id'] in seen_ids:
                    continue
                selected.append(format_chunk_match(chunk, 8, ['graph expansion']))
                seen_ids.add(chunk['id'])
                if len(selected) >= limit:
                    break
            if len(selected) >= limit:
                break

    return selected[:limit]


def build_project_vocabulary(chunks: list[dict]) -> dict:
    token_counts = Counter()
    cooccurrence: dict[str, Counter] = defaultdict(Counter)

    for chunk in chunks:
        chunk_tokens = sorted({
            token
            for token in tokenize(' '.join([
                chunk['path'],
                *chunk.get('signals', []),
                chunk.get('preview', ''),
            ]))
            if len(token) >= 2
        })
        if not chunk_tokens:
            continue
        token_counts.update(chunk_tokens)
        for token in chunk_tokens:
            for related in chunk_tokens:
                if related == token:
                    continue
                cooccurrence[token][related] += 1

    top_terms = [
        term
        for term, _ in token_counts.most_common(160)
    ]
    related_terms = {}
    for term in top_terms:
        ranked_related = [
            related
            for related, _ in cooccurrence[term].most_common(10)
            if related != term
        ]
        if ranked_related:
            related_terms[term] = ranked_related[:6]

    return {
        'topTerms': top_terms[:160],
        'relatedTerms': related_terms,
    }


def score_chunk(
    chunk: dict,
    query_tokens: set[str],
    important_ranks: dict[str, int],
    recent_changed: set[str],
    task: str,
) -> tuple[int, list[str]]:
    score = 0
    reasons = []
    path = chunk['path']
    kind = chunk.get('kind', '')
    haystack = ' '.join([
        path,
        kind,
        ' '.join(chunk.get('signals', [])),
        chunk.get('preview', ''),
    ]).lower()
    config_query = is_config_query(query_tokens)
    manifest_like = is_manifest_like_path(path)
    documentation_like = is_documentation_path(path)

    overlap = sorted(token for token in query_tokens if token in haystack)
    overlap_count = len(overlap)
    token_count = max(len(query_tokens), 1)
    if overlap:
        score += overlap_count * 12
        reasons.append(f'keyword overlap: {", ".join(overlap[:4])}')
    coverage = overlap_count / token_count
    score += int(coverage * 20)
    if token_count >= 3 and overlap_count <= 1:
        score -= 24
        reasons.append('low query coverage')

    path_rank = important_ranks.get(chunk['path'])
    if path_rank is not None:
        score += max(0, 14 - path_rank)
        reasons.append('important file')

    if chunk['path'] in recent_changed:
        if task in {'bugfix-investigation', 'code-review'}:
            score += 18
            reasons.append('recently changed')

    if task == 'understand-project' and kind in {'section', 'model', 'function'}:
        score += 10
        reasons.append('orientation chunk')
    if task == 'feature-delivery' and kind in {'route', 'function', 'model', 'action-flow'}:
        score += 12
        reasons.append('implementation anchor')
    if task == 'bugfix-investigation' and kind in {'route', 'function'}:
        score += 10
        reasons.append('execution path')
    if task == 'code-review' and kind in {'function', 'model', 'route'}:
        score += 8
        reasons.append('review hotspot')

    if config_query:
        if kind in {'config-flow', 'config-type'}:
            score += 24
            reasons.append('configuration anchor')
        if manifest_like:
            score += 20
            reasons.append('manifest file')
        if documentation_like:
            score -= 16
            reasons.append('documentation downrank for config query')
    elif documentation_like and token_count >= 3 and overlap_count <= 1:
        score -= 20
        reasons.append('documentation downrank')

    if is_probably_test_path(path):
        if task == 'feature-delivery':
            score -= 26
            reasons.append('test file downrank')
        elif task in {'understand-project', 'onboarding'}:
            score -= 14
            reasons.append('test file downrank')

    return score, reasons


def is_config_query(query_tokens: set[str]) -> bool:
    return any(token in CONFIG_QUERY_TOKENS for token in query_tokens)


def is_manifest_like_path(path: str) -> bool:
    lowered = path.replace('\\', '/').lower()
    filename = lowered.rsplit('/', 1)[-1]
    suffix = ''
    if '.' in filename:
        suffix = '.' + filename.rsplit('.', 1)[-1]
    file_tokens = tokenize(filename)
    return suffix in MANIFEST_SUFFIXES or any(token in CONFIG_QUERY_TOKENS for token in file_tokens)


def is_documentation_path(path: str) -> bool:
    lowered = path.replace('\\', '/').lower()
    filename = lowered.rsplit('/', 1)[-1]
    suffix = ''
    if '.' in filename:
        suffix = '.' + filename.rsplit('.', 1)[-1]
    file_tokens = tokenize(filename)
    return suffix in DOC_SUFFIXES or any(token in DOC_NAME_TOKENS for token in file_tokens)


def format_chunk_match(chunk: dict, score: int, reasons: list[str]) -> dict:
    return {
        'id': chunk['id'],
        'path': chunk['path'],
        'kind': chunk['kind'],
        'language': chunk['language'],
        'startLine': chunk['startLine'],
        'endLine': chunk['endLine'],
        'signals': chunk.get('signals', []),
        'preview': chunk.get('preview', ''),
        'score': score,
        'reasons': reasons,
    }


def estimate_vocabulary(chunks: list[dict]) -> int:
    tokens = Counter()
    for chunk in chunks:
        for token in tokenize(' '.join([chunk['path'], *chunk.get('signals', []), chunk.get('preview', '')])):
            tokens[token] += 1
    return len(tokens)


def tokenize(text: str) -> set[str]:
    text = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', text)
    text = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', text)
    return {
        token
        for token in re.findall(r'[A-Za-z][A-Za-z0-9_./-]*|[\u4e00-\u9fff]+|\d+', text.lower())
        if len(token) >= 2 and token not in STOPWORDS
    }
