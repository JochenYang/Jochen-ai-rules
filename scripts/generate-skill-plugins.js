#!/usr/bin/env node
/**
 * Generate plugin entries for marketplace.json
 *
 * Scans skills/, agents/, and commands/ directories and updates marketplace.json.
 * Each entry includes only its specific component type for isolation.
 *
 * Usage: node scripts/generate-skill-plugins.js
 */

const fs = require('fs');
const path = require('path');

const SKILLS_DIR = path.join(__dirname, '..', 'skills');
const AGENTS_DIR = path.join(__dirname, '..', 'agents');
const COMMANDS_DIR = path.join(__dirname, '..', 'commands');
const MARKETPLACE_FILE = path.join(__dirname, '..', '.claude-plugin', 'marketplace.json');
const README_FILE = path.join(__dirname, '..', 'README.md');

function extractFrontmatter(filePath) {
  if (!fs.existsSync(filePath)) {
    return null;
  }
  const content = fs.readFileSync(filePath, 'utf-8');
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return null;

  const fm = {};
  for (const line of match[1].split('\n')) {
    const [key, ...vals] = line.split(':');
    if (key && vals.length) {
      fm[key.trim()] = vals.join(':').trim();
    }
  }
  return fm;
}

function getAllSkills() {
  return fs.readdirSync(SKILLS_DIR)
    .filter(f => fs.statSync(path.join(SKILLS_DIR, f)).isDirectory())
    .map(dir => {
      const fm = extractFrontmatter(path.join(SKILLS_DIR, dir, 'SKILL.md'));
      return fm ? { name: fm.name || dir, description: fm.description || '', directory: dir } : null;
    })
    .filter(Boolean);
}

function getAllAgents() {
  return fs.readdirSync(AGENTS_DIR)
    .filter(f => f.endsWith('.md'))
    .map(file => {
      const fm = extractFrontmatter(path.join(AGENTS_DIR, file));
      const name = fm?.name || file.replace('.md', '');
      return fm ? { name: `agent-${name}`, description: fm.description || '', file } : null;
    })
    .filter(Boolean);
}

function getAllCommands() {
  return fs.readdirSync(COMMANDS_DIR)
    .filter(f => f.endsWith('.md'))
    .map(file => {
      const fm = extractFrontmatter(path.join(COMMANDS_DIR, file));
      const name = fm?.argumentHint
        ? file.replace('.md', '')
        : (fm?.name || file.replace('.md', ''));
      return fm ? { name: `command-${name}`, description: fm.description || '', file } : null;
    })
    .filter(Boolean);
}

function buildPluginEntry(name, description, source, componentField, componentPath) {
  return {
    name,
    version: "1.0.0",
    source,
    description,
    [componentField]: [componentPath],
    author: { name: "Jochen" },
    homepage: "https://github.com/JochenYang/Jochen-ai-rules",
    repository: "https://github.com/JochenYang/Jochen-ai-rules",
    license: "MIT",
    category: componentField === 'skills' ? 'skill' : componentField === 'agents' ? 'agent' : 'command',
    tags: [name]
  };
}

function updateMarketplaceJson(skills, agents, commands) {
  let marketplace;
  try {
    marketplace = JSON.parse(fs.readFileSync(MARKETPLACE_FILE, 'utf-8'));
  } catch (e) {
    marketplace = {
      name: "jochen-ai-rules",
      owner: { name: "Jochen", email: "dayantv666@gmail.com" },
      metadata: { description: "Jochen's AI development ruleset", version: "1.2.9" },
      plugins: []
    };
  }

  // Remove old skill/agent/command entries (keep jochen-ai-rules bundle)
  const bundle = marketplace.plugins.find(p => p.name === 'jochen-ai-rules');
  marketplace.plugins = bundle ? [bundle] : [];

  // Add skill entries
  for (const s of skills) {
    marketplace.plugins.push(buildPluginEntry(
      s.name, s.description, `./skills/${s.name}/`, 'skills', `./skills/${s.name}/`
    ));
  }

  // Add agent entries
  for (const a of agents) {
    marketplace.plugins.push(buildPluginEntry(
      a.name, a.description, './agents/', 'agents', `./agents/${a.file}`
    ));
  }

  // Add command entries
  for (const c of commands) {
    marketplace.plugins.push(buildPluginEntry(
      c.name, c.description, './commands/', 'commands', `./commands/${c.file}`
    ));
  }

  fs.writeFileSync(MARKETPLACE_FILE, JSON.stringify(marketplace, null, 2) + '\n');
  return marketplace.plugins.length;
}

function updateReadme(skills, agents, commands) {
  let readme = fs.readFileSync(README_FILE, 'utf-8');

  const skillList = skills.map(s => `/plugin install ${s.name}`).join('\n');
  const agentList = agents.map(a => `/plugin install ${a.name}`).join('\n');
  const commandList = commands.map(c => `/plugin install ${c.name}`).join('\n');

  const newInstallSection = `### Option 1: From Marketplace (Recommended)

\`\`\`bash
# Add the marketplace
/plugin marketplace add JochenYang/Jochen-ai-rules

# Install ALL (full bundle with agents, commands, skills, hooks)
/plugin install jochen-ai-rules

# Install individual skills:
${skillList}

# Install individual agents:
${agentList}

# Install individual commands:
${commandList}
\`\`\``;

  readme = readme.replace(/### Option 1: From Marketplace \(Recommended\)[\s\S]*?(?=### Option 2:)/, newInstallSection + '\n\n');
  fs.writeFileSync(README_FILE, readme);
}

function main() {
  console.log('Generating plugin entries...\n');

  const skills = getAllSkills();
  const agents = getAllAgents();
  const commands = getAllCommands();

  console.log(`Found ${skills.length} skills, ${agents.length} agents, ${commands.length} commands\n`);

  const totalPlugins = updateMarketplaceJson(skills, agents, commands);
  console.log(`Updated marketplace.json with ${totalPlugins} plugins`);

  updateReadme(skills, agents, commands);
  console.log('Updated README.md');

  console.log('\nDone!');
}

main();
