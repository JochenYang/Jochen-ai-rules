#!/usr/bin/env node

const fs = require('node:fs');
const path = require('node:path');
const Module = require('node:module');

function unique(list) {
  return Array.from(new Set(list.filter(Boolean)));
}

function resolveTypeScript(projectPath) {
  const candidates = [];
  const localNodeModules = path.join(projectPath, 'node_modules');
  candidates.push(localNodeModules);
  candidates.push(process.cwd());
  candidates.push(__dirname);

  for (const candidate of candidates) {
    try {
      return require(require.resolve('typescript', { paths: [candidate] }));
    } catch (_error) {
      // continue
    }
  }

  return null;
}

function stringLiteral(node) {
  if (!node) {
    return null;
  }
  if (node.kind === ts.SyntaxKind.StringLiteral || node.kind === ts.SyntaxKind.NoSubstitutionTemplateLiteral) {
    return node.text;
  }
  return null;
}

function frameworkHintsFromImport(specifier) {
  const mapping = {
    react: 'React',
    next: 'Next.js',
    vue: 'Vue',
    express: 'Express',
    '@nestjs/common': 'NestJS',
    '@nestjs/core': 'NestJS',
    '@angular/core': 'Angular',
    svelte: 'Svelte',
  };
  return mapping[specifier] ? [mapping[specifier]] : [];
}

const relPath = process.argv[2];
const projectPath = process.argv[3] || process.cwd();
const sourceText = fs.readFileSync(0, 'utf8');
const ts = resolveTypeScript(projectPath);

if (!ts) {
  process.stdout.write(JSON.stringify({ ok: false, reason: 'typescript compiler unavailable' }));
  process.exit(0);
}

const scriptKindByExt = {
  '.js': ts.ScriptKind.JS,
  '.jsx': ts.ScriptKind.JSX,
  '.ts': ts.ScriptKind.TS,
  '.tsx': ts.ScriptKind.TSX,
};
const ext = path.extname(relPath).toLowerCase();
const sourceFile = ts.createSourceFile(
  relPath,
  sourceText,
  ts.ScriptTarget.Latest,
  true,
  scriptKindByExt[ext] || ts.ScriptKind.TS,
);

const imports = [];
const exportsFound = [];
const apiRoutes = [];
const dataModels = [];
const keyFunctions = [];
const frameworkHints = [];

let controllerPrefix = null;

function hasExportModifier(node) {
  return Array.isArray(node.modifiers) && node.modifiers.some((modifier) => modifier.kind === ts.SyntaxKind.ExportKeyword);
}

function visitDecoratorRoutes(node, inheritedPrefix = null) {
  if (!Array.isArray(node.decorators)) {
    return;
  }

  for (const decorator of node.decorators) {
    if (!ts.isCallExpression(decorator.expression)) {
      continue;
    }
    const expression = decorator.expression.expression;
    const routeArg = decorator.expression.arguments[0];
    const pathValue = stringLiteral(routeArg) || '';

    if (ts.isIdentifier(expression) && expression.text === 'Controller') {
      controllerPrefix = pathValue || '';
      continue;
    }

    if (ts.isIdentifier(expression)) {
      const method = expression.text.toUpperCase();
      if (['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'].includes(method)) {
        const fullPath = `${inheritedPrefix || controllerPrefix || ''}${pathValue}` || pathValue;
        apiRoutes.push({
          method,
          path: fullPath || '/',
          line: sourceFile.getLineAndCharacterOfPosition(decorator.expression.getStart(sourceFile)).line + 1,
        });
      }
    }
  }
}

function collectVariableFunction(node) {
  if (!ts.isVariableStatement(node)) {
    return;
  }
  const exported = hasExportModifier(node);
  for (const declaration of node.declarationList.declarations) {
    if (!ts.isIdentifier(declaration.name)) {
      continue;
    }
    const initializer = declaration.initializer;
    if (!initializer || (!ts.isArrowFunction(initializer) && !ts.isFunctionExpression(initializer))) {
      continue;
    }
    if (exported) {
      exportsFound.push(declaration.name.text);
    }
    keyFunctions.push({
      name: declaration.name.text,
      file: relPath,
      line: sourceFile.getLineAndCharacterOfPosition(declaration.name.getStart(sourceFile)).line + 1,
    });
  }
}

function collectCallRoutes(node) {
  if (!ts.isCallExpression(node)) {
    return;
  }
  if (!ts.isPropertyAccessExpression(node.expression)) {
    return;
  }

  const method = node.expression.name.text.toLowerCase();
  const target = node.expression.expression.getText(sourceFile);
  if (!['app', 'router'].includes(target) || !['get', 'post', 'put', 'delete', 'patch', 'head', 'options'].includes(method)) {
    return;
  }

  const pathValue = stringLiteral(node.arguments[0]);
  if (pathValue) {
    apiRoutes.push({
      method: method.toUpperCase(),
      path: pathValue,
      line: sourceFile.getLineAndCharacterOfPosition(node.expression.name.getStart(sourceFile)).line + 1,
    });
  }
}

function visit(node, inheritedPrefix = null) {
  if (ts.isImportDeclaration(node) && node.moduleSpecifier) {
    const specifier = node.moduleSpecifier.text;
    imports.push(specifier);
    frameworkHints.push(...frameworkHintsFromImport(specifier));
  }

  if (ts.isFunctionDeclaration(node) && node.name) {
    if (hasExportModifier(node)) {
      exportsFound.push(node.name.text);
    }
    keyFunctions.push({
      name: node.name.text,
      file: relPath,
      line: sourceFile.getLineAndCharacterOfPosition(node.name.getStart(sourceFile)).line + 1,
    });
    visitDecoratorRoutes(node, inheritedPrefix);
  }

  if (ts.isClassDeclaration(node) && node.name) {
    if (hasExportModifier(node)) {
      exportsFound.push(node.name.text);
    }
    dataModels.push({
      name: node.name.text,
      type: 'class',
      line: sourceFile.getLineAndCharacterOfPosition(node.name.getStart(sourceFile)).line + 1,
    });
    visitDecoratorRoutes(node, inheritedPrefix);

    const classPrefix = controllerPrefix;
    node.members.forEach((member) => {
      if (ts.isMethodDeclaration(member) && member.name && ts.isIdentifier(member.name)) {
        keyFunctions.push({
          name: member.name.text,
          file: relPath,
          line: sourceFile.getLineAndCharacterOfPosition(member.name.getStart(sourceFile)).line + 1,
        });
        visitDecoratorRoutes(member, classPrefix);
      }
    });
    controllerPrefix = null;
  }

  if (ts.isInterfaceDeclaration(node)) {
    if (hasExportModifier(node)) {
      exportsFound.push(node.name.text);
    }
    dataModels.push({
      name: node.name.text,
      type: 'interface',
      line: sourceFile.getLineAndCharacterOfPosition(node.name.getStart(sourceFile)).line + 1,
    });
  }

  if (ts.isTypeAliasDeclaration(node)) {
    if (hasExportModifier(node)) {
      exportsFound.push(node.name.text);
    }
    dataModels.push({
      name: node.name.text,
      type: 'type',
      line: sourceFile.getLineAndCharacterOfPosition(node.name.getStart(sourceFile)).line + 1,
    });
  }

  collectVariableFunction(node);
  collectCallRoutes(node);
  ts.forEachChild(node, (child) => visit(child, inheritedPrefix));
}

visit(sourceFile);

process.stdout.write(
  JSON.stringify({
    ok: true,
    engine: 'typescript-ast',
    confidence: 'high',
    imports: unique(imports).slice(0, 8),
    exports: unique(exportsFound).slice(0, 8),
    apiRoutes,
    dataModels,
    keyFunctions,
    frameworkHints: unique(frameworkHints),
    warnings: [],
  }),
);
