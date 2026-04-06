from pathlib import Path

SNAPSHOT_VERSION = '3.0'
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

# Feature flags for advanced chunking modes
USE_SEMANTIC_CHUNKING = False
USE_INCREMENTAL_MODE = False
USE_SQLITE_INDEX = True

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
