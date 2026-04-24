from __future__ import annotations

import ast
import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


HTTP_METHODS = {'get', 'post', 'put', 'delete', 'patch', 'head', 'options'}
TS_EXTENSIONS = {'.ts', '.tsx', '.js', '.jsx'}
LOCAL_IMPORT_ROOTS = {'src', 'app', 'components', 'lib', 'libs', 'shared', 'utils', 'services', 'stores', 'modules'}


@dataclass
class FileAnalysis:
    imports: list[str] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)
    api_routes: list[dict] = field(default_factory=list)
    data_models: list[dict] = field(default_factory=list)
    key_functions: list[dict] = field(default_factory=list)
    framework_hints: list[str] = field(default_factory=list)
    engine: str = 'none'
    confidence: str = 'none'
    warnings: list[str] = field(default_factory=list)


def clean_content_for_parsing(content: str, ext: str) -> str:
    """Remove common comments to reduce regex false positives."""
    if ext == '.py':
        return re.sub(r'^\s*#.*$', '', content, flags=re.MULTILINE)

    if ext in TS_EXTENSIONS:
        without_blocks = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        return re.sub(r'^\s*//.*$', '', without_blocks, flags=re.MULTILINE)

    return content


class PythonAstAnalyzer:
    def supports(self, ext: str) -> bool:
        return ext == '.py'

    def analyze(self, content: str, rel_path: str) -> FileAnalysis:
        result = FileAnalysis(engine='python-ast', confidence='high')

        try:
            tree = ast.parse(content, filename=rel_path)
        except SyntaxError as exc:
            result.engine = 'python-regex-fallback'
            result.confidence = 'medium'
            result.warnings.append(f'python syntax error: {exc.msg}')
            return _regex_python_analysis(content, rel_path, result)

        framework_hints = set()
        exports = set()
        imports = set()
        routes: list[dict] = []
        models: list[dict] = []
        functions: list[dict] = []

        explicit_all = _extract_python_dunder_all(tree)

        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name.split('.')[0]
                    imports.add(alias.name)
                    framework_hints.update(_framework_hints_from_python_import(name))
            elif isinstance(node, ast.ImportFrom):
                module = (node.module or '').split('.')[0]
                if node.module:
                    imports.add(node.module)
                if module:
                    framework_hints.update(_framework_hints_from_python_import(module))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith('_'):
                    functions.append({
                        'name': node.name,
                        'file': rel_path,
                        'line': node.lineno,
                    })
                    routes.extend(_extract_python_routes_from_function(node))
                    exports.add(node.name)
            elif isinstance(node, ast.ClassDef):
                if not node.name.startswith('_'):
                    exports.add(node.name)
                model_type = _classify_python_model(node)
                if model_type:
                    models.append({'name': node.name, 'type': model_type, 'line': node.lineno})

        if explicit_all:
            exports = {name for name in exports if name in explicit_all}

        result.imports = _prioritize_imports(imports)
        result.exports = sorted(exports)[:8]
        result.api_routes = routes
        result.data_models = models
        result.key_functions = functions
        result.framework_hints = sorted(framework_hints)
        return result


class JavaScriptAnalyzer:
    def __init__(self, bridge_path: Path):
        self.bridge_path = bridge_path

    def supports(self, ext: str) -> bool:
        return ext in TS_EXTENSIONS

    def analyze(self, content: str, rel_path: str, project_path: str) -> FileAnalysis:
        ast_result = self._analyze_with_typescript_ast(content, rel_path, project_path)
        if ast_result is not None:
            return ast_result

        fallback = FileAnalysis(
            engine='typescript-regex-fallback',
            confidence='medium',
            warnings=['typescript compiler unavailable; used regex fallback'],
        )
        return _regex_typescript_analysis(content, rel_path, fallback)

    def _analyze_with_typescript_ast(
        self,
        content: str,
        rel_path: str,
        project_path: str,
    ) -> FileAnalysis | None:
        try:
            completed = subprocess.run(
                [
                    'node',
                    str(self.bridge_path),
                    rel_path,
                    project_path,
                ],
                input=content,
                text=True,
                capture_output=True,
                check=False,
            )
        except Exception:
            return None

        if completed.returncode != 0:
            return None

        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError:
            return None

        if not payload.get('ok'):
            return None

        return FileAnalysis(
            imports=_prioritize_imports(payload.get('imports', [])),
            exports=payload.get('exports', [])[:8],
            api_routes=payload.get('apiRoutes', []),
            data_models=payload.get('dataModels', []),
            key_functions=payload.get('keyFunctions', []),
            framework_hints=payload.get('frameworkHints', []),
            engine=payload.get('engine', 'typescript-ast'),
            confidence=payload.get('confidence', 'high'),
            warnings=payload.get('warnings', []),
        )


from .multi_lang_analyzer import MultiLangAnalyzer

class AnalyzerRegistry:
    def __init__(self, bridge_path: Path):
        self.python = PythonAstAnalyzer()
        self.javascript = JavaScriptAnalyzer(bridge_path)
        self.multi = MultiLangAnalyzer()

    def analyze_file(self, content: str | None, rel_path: str, project_path: str) -> FileAnalysis:
        if content is None:
            return FileAnalysis()

        ext = Path(rel_path).suffix.lower()
        if self.python.supports(ext):
            return self.python.analyze(content, rel_path)
        if self.javascript.supports(ext):
            return self.javascript.analyze(content, rel_path, project_path)
        if self.multi.supports(ext):
            return self._normalize_multi_result(self.multi.analyze(content, rel_path))
        return FileAnalysis()

    def _normalize_multi_result(self, payload: object) -> FileAnalysis:
        if isinstance(payload, FileAnalysis):
            return payload
        if not isinstance(payload, dict):
            return FileAnalysis(engine='multi-lang-fallback', confidence='low')

        normalized_key_functions = []
        for item in payload.get('key_functions', []):
            if isinstance(item, dict):
                name = item.get('name')
                line = item.get('line')
                if not isinstance(name, str) or not name.strip():
                    continue
                if not isinstance(line, int) or line <= 0:
                    line = 1
                normalized_key_functions.append({
                    'name': name,
                    'file': item.get('file') or payload.get('path'),
                    'line': line,
                })
                continue

            name = str(item).strip()
            if not name:
                continue
            normalized_key_functions.append({
                'name': name,
                'file': payload.get('path'),
                'line': 1,
            })

        return FileAnalysis(
            imports=_prioritize_imports(payload.get('imports', [])),
            exports=[item for item in payload.get('exports', []) if isinstance(item, str)][:8],
            api_routes=[item for item in payload.get('api_routes', []) if isinstance(item, dict)],
            data_models=[item for item in payload.get('data_models', []) if isinstance(item, dict)],
            key_functions=normalized_key_functions[:12],
            framework_hints=[item for item in payload.get('framework_hints', []) if isinstance(item, str)][:8],
            engine='multi-lang-regex',
            confidence='medium',
            warnings=[],
        )


def _framework_hints_from_python_import(module: str) -> set[str]:
    mapping = {
        'fastapi': 'FastAPI',
        'flask': 'Flask',
        'django': 'Django',
        'pydantic': 'Pydantic',
        'sqlalchemy': 'SQLAlchemy',
    }
    return {mapping[module]} if module in mapping else set()


def _extract_python_dunder_all(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == '__all__':
                if isinstance(node.value, (ast.List, ast.Tuple, ast.Set)):
                    for item in node.value.elts:
                        if isinstance(item, ast.Constant) and isinstance(item.value, str):
                            names.add(item.value)
    return names


def _classify_python_model(node: ast.ClassDef) -> str | None:
    base_names = {_python_name(base) for base in node.bases}

    if 'BaseModel' in base_names:
        return 'pydantic'
    if 'models.Model' in base_names or 'Model' in base_names:
        return 'django-model'
    if 'Base' in base_names or 'DeclarativeBase' in base_names:
        return 'sqlalchemy'
    if any(
        isinstance(decorator, ast.Name) and decorator.id == 'dataclass'
        or isinstance(decorator, ast.Attribute) and decorator.attr == 'dataclass'
        for decorator in node.decorator_list
    ):
        return 'dataclass'
    return None


def _extract_python_routes_from_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[dict]:
    routes: list[dict] = []

    for decorator in node.decorator_list:
        if not isinstance(decorator, ast.Call):
            continue

        func = decorator.func
        if isinstance(func, ast.Attribute):
            attr_name = func.attr.lower()
            if attr_name in HTTP_METHODS:
                path = _string_literal(decorator.args[0]) if decorator.args else None
                if path:
                    routes.append({'method': attr_name.upper(), 'path': path, 'line': node.lineno})
                continue

            if attr_name == 'route':
                path = _string_literal(decorator.args[0]) if decorator.args else None
                if not path:
                    continue

                methods = None
                for keyword in decorator.keywords:
                    if keyword.arg == 'methods':
                        methods = _extract_python_methods(keyword.value)
                        break

                if not methods:
                    routes.append({'method': 'GET', 'path': path, 'line': node.lineno})
                else:
                    for method in methods:
                        routes.append({'method': method, 'path': path, 'line': node.lineno})

    return routes


def _extract_python_methods(node: ast.AST) -> list[str]:
    if not isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return []

    methods = []
    for item in node.elts:
        value = _string_literal(item)
        if value:
            methods.append(value.upper())
    return methods


def _string_literal(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        constant_parts = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                constant_parts.append(value.value)
            else:
                return None
        return ''.join(constant_parts)
    return None


def _python_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _python_name(node.value)
        return f'{base}.{node.attr}' if base else node.attr
    if isinstance(node, ast.Subscript):
        return _python_name(node.value)
    if isinstance(node, ast.Call):
        return _python_name(node.func)
    return ''


def _regex_python_analysis(content: str, rel_path: str, result: FileAnalysis) -> FileAnalysis:
    cleaned = clean_content_for_parsing(content, '.py')

    imports = set(re.findall(r'^\s*from\s+([A-Za-z0-9_\.]+)\s+import', cleaned, flags=re.MULTILINE))
    imports.update(re.findall(r'^\s*import\s+([A-Za-z0-9_\.]+)', cleaned, flags=re.MULTILINE))
    result.imports = _prioritize_imports(imports)

    exports = set(re.findall(r'^\s*(?:async\s+)?def\s+([A-Za-z_]\w*)\s*\(', cleaned, flags=re.MULTILINE))
    exports.update(re.findall(r'^\s*class\s+([A-Za-z_]\w*)', cleaned, flags=re.MULTILINE))
    result.exports = sorted(name for name in exports if not name.startswith('_'))[:8]

    for match in re.finditer(r'^\s*@(app|router)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']', cleaned, flags=re.MULTILINE):
        result.api_routes.append({'method': match.group(2).upper(), 'path': match.group(3), 'line': _line_number_for_offset(cleaned, match.start())})

    flask_pattern = r'^\s*@(app|blueprint)\.route\(\s*["\']([^"\']+)["\'](?P<args>[^)]*)\)'
    for match in re.finditer(flask_pattern, cleaned, flags=re.MULTILINE):
        methods = re.search(r'methods\s*=\s*\[([^\]]+)\]', match.group('args'))
        if not methods:
            result.api_routes.append({'method': 'GET', 'path': match.group(2), 'line': _line_number_for_offset(cleaned, match.start())})
            continue
        for raw_method in re.findall(r'["\']([A-Za-z]+)["\']', methods.group(1)):
            result.api_routes.append({'method': raw_method.upper(), 'path': match.group(2), 'line': _line_number_for_offset(cleaned, match.start())})

    for match in re.finditer(r'class\s+(\w+)\s*\(\s*BaseModel', cleaned):
        result.data_models.append({'name': match.group(1), 'type': 'pydantic', 'line': _line_number_for_offset(cleaned, match.start())})
    for match in re.finditer(r'class\s+(\w+)\s*\(\s*models\.Model', cleaned):
        result.data_models.append({'name': match.group(1), 'type': 'django-model', 'line': _line_number_for_offset(cleaned, match.start())})
    for match in re.finditer(r'class\s+(\w+)\s*\(\s*(?:Base|DeclarativeBase)', cleaned):
        result.data_models.append({'name': match.group(1), 'type': 'sqlalchemy', 'line': _line_number_for_offset(cleaned, match.start())})

    for i, line in enumerate(content.splitlines(), start=1):
        match = re.search(r'(?:async\s+)?def\s+(\w+)\s*\(', line)
        if match and not match.group(1).startswith('_'):
            result.key_functions.append({'name': match.group(1), 'file': rel_path, 'line': i})

    framework_hints = set()
    for module_name in result.imports:
        framework_hints.update(_framework_hints_from_python_import(module_name.split('.')[0]))
    result.framework_hints = sorted(framework_hints)
    return result


def _regex_typescript_analysis(content: str, rel_path: str, result: FileAnalysis) -> FileAnalysis:
    cleaned = clean_content_for_parsing(content, Path(rel_path).suffix.lower())

    imports = set(re.findall(r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]', cleaned))
    imports.update(re.findall(r'require\(\s*[\'"]([^\'"]+)[\'"]\s*\)', cleaned))
    result.imports = _prioritize_imports(imports)

    exports = set(re.findall(r'export\s+(?:async\s+)?function\s+(\w+)', cleaned))
    exports.update(re.findall(r'export\s+class\s+(\w+)', cleaned))
    exports.update(re.findall(r'export\s+(?:const|let|var)\s+(\w+)', cleaned))
    exports.update(re.findall(r'export\s+interface\s+(\w+)', cleaned))
    exports.update(re.findall(r'export\s+type\s+(\w+)', cleaned))
    result.exports = sorted(exports)[:8]

    express_pattern = r'(?:app|router)\.(get|post|put|delete|patch|head|options)\s*\(\s*[\'"]([^\'"]+)[\'"]'
    for match in re.finditer(express_pattern, cleaned, re.IGNORECASE):
        result.api_routes.append({'method': match.group(1).upper(), 'path': match.group(2)})

    nestjs_pattern = r'^\s*@(Get|Post|Put|Delete|Patch|Head|Options)\s*\(\s*[\'"]([^\'"]+)[\'"]'
    for match in re.finditer(nestjs_pattern, cleaned, re.IGNORECASE | re.MULTILINE):
        result.api_routes.append({'method': match.group(1).upper(), 'path': match.group(2)})

    for match in re.finditer(r'(?:export\s+)?interface\s+(\w+)', cleaned):
        result.data_models.append({'name': match.group(1), 'type': 'interface'})
    for match in re.finditer(r'(?:export\s+)?type\s+(\w+)\s*=', cleaned):
        result.data_models.append({'name': match.group(1), 'type': 'type'})
    for match in re.finditer(r'(?:export\s+)?class\s+(\w+)', cleaned):
        result.data_models.append({'name': match.group(1), 'type': 'class'})

    for i, line in enumerate(content.splitlines(), start=1):
        match = re.search(r'export\s+(?:async\s+)?function\s+(\w+)', line)
        if match:
            result.key_functions.append({'name': match.group(1), 'file': rel_path, 'line': i})
            continue

        match = re.search(r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(', line)
        if match:
            result.key_functions.append({'name': match.group(1), 'file': rel_path, 'line': i})

    framework_hints = set()
    for imported in result.imports:
        framework_hints.update(_framework_hints_from_js_import(imported))
    result.framework_hints = sorted(framework_hints)
    return result


def _framework_hints_from_js_import(import_name: str) -> set[str]:
    mapping = {
        'react': 'React',
        'next': 'Next.js',
        'vue': 'Vue',
        '@nestjs/common': 'NestJS',
        '@nestjs/core': 'NestJS',
        'express': 'Express',
        '@angular/core': 'Angular',
        'svelte': 'Svelte',
    }
    return {mapping[import_name]} if import_name in mapping else set()


def _prioritize_imports(imports: list[str] | set[str], limit: int = 24) -> list[str]:
    def sort_key(import_name: str) -> tuple[int, str]:
        return (0 if _is_localish_import(import_name) else 1, import_name)

    normalized = [item for item in imports if isinstance(item, str) and item]
    return sorted(set(normalized), key=sort_key)[:limit]


def _is_localish_import(import_name: str) -> bool:
    if import_name.startswith(('.', '/', '@/', '~/')):
        return True

    head = import_name.split('/', 1)[0]
    return head in LOCAL_IMPORT_ROOTS


def _line_number_for_offset(content: str, offset: int) -> int:
    return content.count('\n', 0, offset) + 1
