from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / 'scripts'
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import generate  # noqa: E402


def make_snapshot() -> tuple[dict, dict]:
    snapshot = {
        'freshness': {'snapshotPath': 'repo/progress/context-codebase.json'},
        'sourceFingerprint': 'demo-fingerprint',
        'analysis': {'warnings': []},
        'summary': {
            'name': 'demo-project',
            'type': 'Backend Service',
            'entryPoints': ['src/main/router.ts'],
        },
        'contextHints': {
            'recommendedStart': 'src/main/router.ts',
            'readOrder': ['src/main/router.ts', 'src/services/message-service.ts'],
            'highSignalAreas': ['src/main/', 'src/services/'],
        },
        'modules': {
            'src/main/': 'routing entry area',
            'src/services/': 'business logic',
            'src/config/': 'configuration module',
            '.claude-plugin/': 'plugin release metadata',
            'ops/': 'automation and release manifests',
        },
        'fileTree': {
            './': ['README.md'],
            'src/main/': ['router.ts'],
            'src/services/': ['message-service.ts'],
            'src/config/': ['message-config.ts'],
            '.claude-plugin/': ['plugin.json'],
            'ops/': ['release-workflow.yml'],
            'docs/': ['release-guide.md'],
        },
        'retrieval': {
            'defaultTask': 'understand-project',
            'availableTasks': [
                'understand-project',
                'feature-delivery',
                'bugfix-investigation',
                'code-review',
                'onboarding',
            ],
            'projectVocabulary': {
                'relatedTerms': {
                    'message': ['dispatch', 'routing', 'router'],
                    'routing': ['route', 'dispatch', 'handler'],
                    'config': ['settings', 'schema'],
                    'plugin': ['version', 'metadata'],
                }
            },
        },
        'contextPacks': {
            'understand-project': {
                'description': 'Orient a new model to the project quickly.',
                'chunks': [],
                'files': ['src/main/router.ts'],
            },
            'bugfix-investigation': {
                'description': 'Trace failure paths and surrounding code.',
                'chunks': [],
                'files': ['src/main/router.ts', 'src/services/message-service.ts'],
            },
            'feature-delivery': {
                'description': 'Add or extend behavior using existing structure.',
                'chunks': [],
                'files': ['src/main/router.ts', 'src/services/message-service.ts'],
            },
            'code-review': {
                'description': 'Review touched areas and nearby risks.',
                'chunks': [],
                'files': ['src/main/router.ts'],
            },
            'onboarding': {
                'description': 'Help a new engineer navigate the codebase.',
                'chunks': [],
                'files': ['README.md', 'src/main/router.ts'],
            },
        },
        'importantFiles': [
            {
                'path': 'src/main/router.ts',
                'role': 'Routing / transport',
                'language': 'TypeScript',
                'lines': 120,
                'whyImportant': 'routes incoming messages',
                'score': 95,
            },
            {
                'path': 'src/services/message-service.ts',
                'role': 'Service',
                'language': 'TypeScript',
                'lines': 88,
                'whyImportant': 'handles message processing',
                'score': 90,
            },
            {
                'path': 'src/config/message-config.ts',
                'role': 'Configuration',
                'language': 'TypeScript',
                'lines': 42,
                'whyImportant': 'stores routing configuration',
                'score': 82,
            },
            {
                'path': '.claude-plugin/plugin.json',
                'role': 'Configuration',
                'language': 'JSON',
                'lines': 12,
                'whyImportant': 'plugin release metadata',
                'score': 86,
            },
            {
                'path': 'README.md',
                'role': 'Project overview',
                'language': 'Markdown',
                'lines': 30,
                'whyImportant': 'project overview',
                'score': 60,
            },
            {
                'path': 'ops/release-workflow.yml',
                'role': 'Configuration',
                'language': 'YAML',
                'lines': 28,
                'whyImportant': 'release workflow manifest',
                'score': 78,
            },
        ],
        'representativeSnippets': [],
        'graph': {
            'fileDependencies': [
                {'path': 'src/main/router.ts', 'dependsOn': ['src/services/message-service.ts']},
                {'path': 'src/services/message-service.ts', 'dependsOn': ['src/config/message-config.ts']},
            ],
            'hotspots': [
                {'path': 'src/main/router.ts', 'inbound': 3, 'outbound': 2, 'signals': 4},
                {'path': 'src/services/message-service.ts', 'inbound': 2, 'outbound': 2, 'signals': 3},
                {'path': 'src/config/message-config.ts', 'inbound': 1, 'outbound': 1, 'signals': 2},
                {'path': '.claude-plugin/plugin.json', 'inbound': 1, 'outbound': 0, 'signals': 2},
                {'path': 'ops/release-workflow.yml', 'inbound': 1, 'outbound': 0, 'signals': 2},
            ],
            'moduleDependencies': [
                {'from': 'src/main/', 'to': 'src/services/', 'strength': 2},
            ],
            'pathIndex': [
                {'module': 'src/main/', 'files': [{'path': 'src/main/router.ts'}]},
                {'module': 'src/services/', 'files': [{'path': 'src/services/message-service.ts'}]},
                {'module': 'src/config/', 'files': [{'path': 'src/config/message-config.ts'}]},
                {'module': '.claude-plugin/', 'files': [{'path': '.claude-plugin/plugin.json'}]},
                {'module': 'ops/', 'files': [{'path': 'ops/release-workflow.yml'}]},
            ],
        },
        'externalContext': {
            'recentChangedFiles': ['src/main/router.ts'],
            'documentationSources': ['README.md'],
            'decisionSources': [],
            'teamConventions': ['Prefer routing changes through service layer.'],
        },
    }
    index_state = {
        'files': {
            'src/main/router.ts': {'language': 'TypeScript', 'lineCount': 120},
            'src/services/message-service.ts': {'language': 'TypeScript', 'lineCount': 88},
            'src/config/message-config.ts': {'language': 'TypeScript', 'lineCount': 42},
            '.claude-plugin/plugin.json': {'language': 'JSON', 'lineCount': 12},
            'README.md': {'language': 'Markdown', 'lineCount': 30},
            'tests/router.test.ts': {'language': 'TypeScript', 'lineCount': 24},
            'ops/release-workflow.yml': {'language': 'YAML', 'lineCount': 28},
            'docs/release-guide.md': {'language': 'Markdown', 'lineCount': 40},
        },
        'chunks': [
            {
                'id': 'router:1',
                'path': 'src/main/router.ts',
                'kind': 'route',
                'language': 'TypeScript',
                'startLine': 8,
                'endLine': 30,
                'signals': ['dispatchMessage', 'route', 'message'],
                'preview': 'export async function dispatchMessage(message) {\n  return routeIncomingMessage(message)\n}',
                'score': 0,
            },
            {
                'id': 'service:1',
                'path': 'src/services/message-service.ts',
                'kind': 'function',
                'language': 'TypeScript',
                'startLine': 12,
                'endLine': 40,
                'signals': ['handleMessage', 'routing'],
                'preview': 'export function handleMessage(message) {\n  return runRoutingStrategy(message)\n}',
                'score': 0,
            },
            {
                'id': 'config:1',
                'path': 'src/config/message-config.ts',
                'kind': 'config-flow',
                'language': 'TypeScript',
                'startLine': 1,
                'endLine': 20,
                'signals': ['routingConfig', 'config'],
                'preview': 'export const routingConfig = {\n  retryLimit: 3,\n  fallbackChannel: \"default\"\n}',
                'score': 0,
            },
            {
                'id': 'plugin:1',
                'path': '.claude-plugin/plugin.json',
                'kind': 'config-flow',
                'language': 'JSON',
                'startLine': 1,
                'endLine': 12,
                'signals': ['plugin', 'version'],
                'preview': '{\n  \"name\": \"demo-plugin\",\n  \"version\": \"1.2.3\"\n}',
                'score': 0,
            },
            {
                'id': 'docs:1',
                'path': 'README.md',
                'kind': 'section',
                'language': 'Markdown',
                'startLine': 1,
                'endLine': 10,
                'signals': ['overview'],
                'preview': '# Demo Project\nRouting overview.',
                'score': 0,
            },
            {
                'id': 'workflow:1',
                'path': 'ops/release-workflow.yml',
                'kind': 'config-flow',
                'language': 'YAML',
                'startLine': 1,
                'endLine': 16,
                'signals': ['workflow', 'release', 'publish'],
                'preview': 'name: Release Workflow\non:\n  workflow_dispatch:\n  push:\n    tags:\n      - v*',
                'score': 0,
            },
            {
                'id': 'release-doc:1',
                'path': 'docs/release-guide.md',
                'kind': 'section',
                'language': 'Markdown',
                'startLine': 1,
                'endLine': 18,
                'signals': ['release guide', 'workflow'],
                'preview': '# Release Guide\nSee the release workflow and publishing checklist.',
                'score': 0,
            },
            {
                'id': 'test:1',
                'path': 'tests/router.test.ts',
                'kind': 'function',
                'language': 'TypeScript',
                'startLine': 1,
                'endLine': 20,
                'signals': ['dispatchMessage', 'test'],
                'preview': 'test(\"dispatch message\", async () => {\n  expect(true).toBe(true)\n})',
                'score': 0,
            },
        ],
    }
    return snapshot, index_state


class CSRIntegrationTests(unittest.TestCase):
    def init_git_repo(self, base: Path) -> None:
        subprocess.run(['git', 'init'], cwd=base, check=True, capture_output=True, text=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=base, check=True, capture_output=True, text=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=base, check=True, capture_output=True, text=True)

    def test_read_payload_auto_routes_bugfix_query_through_csr(self) -> None:
        snapshot, index_state = make_snapshot()

        payload = generate.build_read_payload(
            snapshot,
            index_state,
            'understand-project',
            '消息路由失败时走的是哪条链路',
        )

        self.assertEqual(payload['task'], 'bugfix-investigation')
        self.assertEqual(payload['contextEngine']['name'], 'miloya-csr')
        self.assertTrue(payload['contextEngine']['enabled'])
        self.assertEqual(payload['contextEngine']['route']['subfocus'], 'execution-path')
        self.assertIn('csr-routed', payload['queryIntent']['labels'])
        self.assertIn('recent-change-boost', payload['contextEngine']['route']['strategies'])
        self.assertEqual(payload['files'][0]['path'], 'src/main/router.ts')
        self.assertIn('src/services/message-service.ts', [item['path'] for item in payload['files']])
        json.dumps(payload, ensure_ascii=False)

    def test_read_payload_merges_csr_scope_notes(self) -> None:
        snapshot, index_state = make_snapshot()

        payload = generate.build_read_payload(
            snapshot,
            index_state,
            'feature-delivery',
            'add message routing config support',
        )

        self.assertTrue(payload['contextEngine']['enabled'])
        self.assertIn('src/config/message-config.ts', payload['searchScope']['preferPaths'])
        self.assertTrue(any('CSR route=' in note for note in payload['searchScope']['notes']))
        self.assertIn(payload['queryProfile'], {'feature', 'config', 'trace'})
        json.dumps(payload, ensure_ascii=False)

    def test_read_payload_uses_dynamic_path_hints_for_hidden_config_paths(self) -> None:
        snapshot, index_state = make_snapshot()

        payload = generate.build_read_payload(
            snapshot,
            index_state,
            'understand-project',
            'plugin 版本号在哪维护',
        )

        self.assertIn('.claude-plugin/', payload['queryIntent']['dynamicPathHints'])
        self.assertEqual(payload['files'][0]['path'], '.claude-plugin/plugin.json')
        json.dumps(payload, ensure_ascii=False)

    def test_scan_files_keeps_hidden_project_files_without_repo_specific_whitelist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            (base / '.meta').mkdir()
            (base / '.meta' / 'config.json').write_text('{}', encoding='utf-8')
            (base / '.git').mkdir()
            (base / '.git' / 'HEAD').write_text('ref: refs/heads/main', encoding='utf-8')
            (base / '.env.example').write_text('KEY=value', encoding='utf-8')

            scanned = [Path(path).relative_to(base).as_posix() for path in generate.scan_files(str(base))]

            self.assertIn('.meta/config.json', scanned)
            self.assertIn('.env.example', scanned)
            self.assertNotIn('.git/HEAD', scanned)

    def test_workflow_query_prefers_manifest_snippets_over_docs(self) -> None:
        snapshot, index_state = make_snapshot()

        payload = generate.build_read_payload(
            snapshot,
            index_state,
            'understand-project',
            'release workflow 在哪定义',
        )

        self.assertEqual(payload['queryProfile'], 'config')
        self.assertEqual(payload['files'][0]['path'], 'ops/release-workflow.yml')
        self.assertEqual(payload['snippets'][0]['path'], 'ops/release-workflow.yml')
        json.dumps(payload, ensure_ascii=False)

    def test_read_payload_uses_sqlite_matches_when_index_chunks_missing(self) -> None:
        snapshot, index_state = make_snapshot()

        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            progress_dir = base / 'repo' / 'progress'
            progress_dir.mkdir(parents=True)
            sqlite_path = progress_dir / 'context-codebase.db'
            sqlite_index = generate.SQLiteIndex(str(sqlite_path))
            sqlite_index.upsert_chunks([
                {
                    'id': 'router:1',
                    'path': 'src/main/router.ts',
                    'startLine': 8,
                    'endLine': 30,
                    'kind': 'route',
                    'name': 'dispatchMessage',
                    'language': 'TypeScript',
                    'signals': ['dispatchMessage', 'route', 'message'],
                    'preview': 'export async function dispatchMessage(message) {\n  return routeIncomingMessage(message)\n}',
                },
                {
                    'id': 'service:1',
                    'path': 'src/services/message-service.ts',
                    'startLine': 12,
                    'endLine': 40,
                    'kind': 'function',
                    'name': 'handleMessage',
                    'language': 'TypeScript',
                    'signals': ['handleMessage', 'routing'],
                    'preview': 'export function handleMessage(message) {\n  return runRoutingStrategy(message)\n}',
                },
            ])

            payload = generate.build_read_payload(
                snapshot,
                {'files': index_state['files'], 'chunks': []},
                'understand-project',
                'message routing',
                sqlite_db_path=str(sqlite_path),
            )

        self.assertEqual(payload['files'][0]['path'], 'src/services/message-service.ts')
        self.assertEqual(payload['snippets'][0]['path'], 'src/services/message-service.ts')
        json.dumps(payload, ensure_ascii=False)

    def test_generate_snapshot_writes_sqlite_index_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            src_dir = base / 'src'
            src_dir.mkdir()
            (src_dir / 'main.py').write_text('def main():\n    return 1\n', encoding='utf-8')

            generate.generate_snapshot(str(base), force=False)

            sqlite_path = base / 'repo' / 'progress' / 'context-codebase.db'
            self.assertTrue(sqlite_path.exists())
            sqlite_index = generate.SQLiteIndex(str(sqlite_path))
            results = sqlite_index.get_by_path('src/main.py')
            self.assertTrue(any('return 1' in result['preview'] for result in results))

    def test_refresh_updates_sqlite_index_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            src_dir = base / 'src'
            src_dir.mkdir()
            source = src_dir / 'main.py'
            source.write_text('def main():\n    return 1\n', encoding='utf-8')

            generate.generate_snapshot(str(base), force=False)
            source.write_text('def main():\n    return 2\n', encoding='utf-8')

            generate.refresh_index(str(base))

            sqlite_path = base / 'repo' / 'progress' / 'context-codebase.db'
            sqlite_index = generate.SQLiteIndex(str(sqlite_path))
            results = sqlite_index.get_by_path('src/main.py')
            self.assertTrue(any('return 2' in result['preview'] for result in results))

    def test_refresh_updates_index_incrementally_without_rebuilding_snapshot_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            src_dir = base / 'src'
            src_dir.mkdir()
            source = src_dir / 'main.py'
            source.write_text('def main():\n    return 1\n', encoding='utf-8')

            initial = generate.generate_snapshot(str(base), force=False)
            initial_summary = json.loads(json.dumps(initial['summary'], ensure_ascii=False))
            initial_modules = json.loads(json.dumps(initial['modules'], ensure_ascii=False))

            source.write_text('def main():\n    return 2\n', encoding='utf-8')
            refreshed = generate.refresh_index(str(base))

            self.assertEqual(refreshed['freshness']['reason'], 'incremental index refreshed')
            self.assertEqual(refreshed['summary'], initial_summary)
            self.assertEqual(refreshed['modules'], initial_modules)

            index_state = generate.load_existing_index_state(base / 'repo' / 'progress' / 'context-codebase.index.json')
            self.assertIsNotNone(index_state)
            previews = [
                chunk['preview']
                for chunk in index_state['chunks']
                if chunk['path'] == 'src/main.py'
            ]
            self.assertTrue(any('return 2' in preview for preview in previews))

    def test_refresh_detects_same_size_same_mtime_content_change_via_hash_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            src_dir = base / 'src'
            src_dir.mkdir()
            source = src_dir / 'main.py'
            original = 'def main():\n    return 1\n'
            updated = 'def main():\n    return 2\n'
            self.assertEqual(len(original), len(updated))
            source.write_text(original, encoding='utf-8')

            generate.generate_snapshot(str(base), force=False)
            stat_before = source.stat()

            source.write_text(updated, encoding='utf-8')
            os.utime(source, ns=(stat_before.st_atime_ns, stat_before.st_mtime_ns))

            refreshed = generate.refresh_index(str(base))

            self.assertEqual(refreshed['freshness']['reason'], 'incremental index refreshed')
            self.assertGreaterEqual(refreshed['freshness']['hashedCandidateFiles'], 1)
            index_state = generate.load_existing_index_state(base / 'repo' / 'progress' / 'context-codebase.index.json')
            self.assertIsNotNone(index_state)
            previews = [
                chunk['preview']
                for chunk in index_state['chunks']
                if chunk['path'] == 'src/main.py'
            ]
            self.assertTrue(any('return 2' in preview for preview in previews))

    def test_refresh_reuses_cached_hashes_when_sources_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            self.init_git_repo(base)
            src_dir = base / 'src'
            src_dir.mkdir()
            (src_dir / 'main.py').write_text('def main():\n    return 1\n', encoding='utf-8')
            subprocess.run(['git', 'add', '.'], cwd=base, check=True, capture_output=True, text=True)
            subprocess.run(['git', 'commit', '-m', 'init'], cwd=base, check=True, capture_output=True, text=True)

            generate.generate_snapshot(str(base), force=False)
            original_hash = generate.compute_file_content_hash

            def fail_on_hash(_: Path) -> str:
                raise AssertionError('refresh should reuse cached hashes when nothing changed')

            try:
                generate.compute_file_content_hash = fail_on_hash
                refreshed = generate.refresh_index(str(base))
            finally:
                generate.compute_file_content_hash = original_hash

            self.assertEqual(refreshed['freshness']['reason'], 'source fingerprint unchanged')
            self.assertEqual(refreshed['freshness']['hashedCandidateFiles'], 0)

    def test_write_snapshot_keeps_stdout_clean_when_sqlite_index_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            output_path = base / 'repo' / 'progress' / 'context-codebase.json'
            snapshot = {'hello': 'world'}
            chunks = [
                {
                    'id': 'chunk-1',
                    'path': 'src/main.py',
                    'startLine': 1,
                    'endLine': 1,
                    'kind': 'section',
                    'language': 'Python',
                    'signals': [],
                    'preview': 'print("ok")',
                }
            ]

            original_sqlite_index = generate.SQLiteIndex

            class FailingSQLiteIndex:
                def __init__(self, *_args, **_kwargs):
                    raise RuntimeError('sqlite init failed')

            stdout_buffer = StringIO()
            stderr_buffer = StringIO()
            try:
                generate.SQLiteIndex = FailingSQLiteIndex
                with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                    generate.write_snapshot(output_path, snapshot, chunks=chunks)
            finally:
                generate.SQLiteIndex = original_sqlite_index

            self.assertEqual(stdout_buffer.getvalue(), '')
            self.assertIn('WARNING: SQLiteIndex failed', stderr_buffer.getvalue())
            self.assertEqual(
                json.loads(output_path.read_text(encoding='utf-8')),
                snapshot,
            )

    def test_read_text_file_preserves_gb18030_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            path = base / 'gb18030-demo.py'
            expected = '# 注释\ndef hello():\n    return "中文内容"\n'
            path.write_bytes(expected.encode('gb18030'))

            actual = generate.read_text_file(path)

            self.assertEqual(actual, expected)

    def test_query_stdin_reads_utf8_input(self) -> None:
        original_stdin = sys.stdin
        try:
            sys.stdin = StringIO('中文 快照 编码\n')
            query = generate.read_query_input(use_stdin=True)
        finally:
            sys.stdin = original_stdin

        self.assertEqual(query, '中文 快照 编码')


if __name__ == '__main__':
    unittest.main()
