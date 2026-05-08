// Sync agent/command/skill counts back into CLAUDE.md
// Usage: node scripts/sync-doc-counts.js

const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const claudeMdPath = path.join(root, 'CLAUDE.md');

function countFiles(patternDir, pattern) {
  const dir = path.join(root, patternDir);
  if (!fs.existsSync(dir)) return 0;

  if (pattern === 'SKILL.md') {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    return entries.filter(e => {
      if (!e.isDirectory()) return false;
      return fs.existsSync(path.join(dir, e.name, 'SKILL.md'));
    }).length;
  }

  return fs.readdirSync(dir)
    .filter(f => f.endsWith('.md') && f !== 'README.md')
    .length;
}

const agents = countFiles('agents', '*.md');
const commands = countFiles('commands', '*.md');
const skills = countFiles('skills', 'SKILL.md');

let content = fs.readFileSync(claudeMdPath, 'utf-8');

const linePattern = /> Total: \d+ commands · \d+ agents · \d+ skills\./;
const replacement = `> Total: ${commands} commands · ${agents} agents · ${skills} skills.`;

if (linePattern.test(content)) {
  content = content.replace(linePattern, replacement);
  fs.writeFileSync(claudeMdPath, content, 'utf-8');
  console.log(`Updated: ${commands} commands · ${agents} agents · ${skills} skills`);
} else {
  console.log('Count line not found in CLAUDE.md — nothing updated.');
}
