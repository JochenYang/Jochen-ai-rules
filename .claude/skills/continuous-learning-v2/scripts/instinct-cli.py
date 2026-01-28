import argparse
import json
import os
import sys
import re
import urllib.request
from pathlib import Path
from datetime import datetime
from collections import defaultdict

HOMUNCULUS_DIR = Path.home() / ".claude" / "homunculus"
INSTINCTS_DIR = HOMUNCULUS_DIR / "instincts"
PERSONAL_DIR = INSTINCTS_DIR / "personal"
INHERITED_DIR = INSTINCTS_DIR / "inherited"
EVOLVED_DIR = HOMUNCULUS_DIR / "evolved"
OBSERVATIONS_FILE = HOMUNCULUS_DIR / "observations.jsonl"

for directory in [PERSONAL_DIR, INHERITED_DIR, EVOLVED_DIR / "skills", EVOLVED_DIR / "commands", EVOLVED_DIR / "agents"]:
    directory.mkdir(parents=True, exist_ok=True)


def parse_instinct_file(content: str) -> list[dict]:
    instincts = []
    current = {}
    in_frontmatter = False
    content_lines = []

    for line in content.split("\n"):
        if line.strip() == "---":
            if in_frontmatter:
                in_frontmatter = False
                if current:
                    current["content"] = "\n".join(content_lines).strip()
                    instincts.append(current)
                    current = {}
                    content_lines = []
            else:
                in_frontmatter = True
                if current:
                    current["content"] = "\n".join(content_lines).strip()
                    instincts.append(current)
                current = {}
                content_lines = []
        elif in_frontmatter:
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key == "confidence":
                    current[key] = float(value)
                else:
                    current[key] = value
        else:
            content_lines.append(line)

    if current:
        current["content"] = "\n".join(content_lines).strip()
        instincts.append(current)

    return [instinct for instinct in instincts if instinct.get("id")]


def load_all_instincts() -> list[dict]:
    instincts = []

    for directory in [PERSONAL_DIR, INHERITED_DIR]:
        if not directory.exists():
            continue
        for file in directory.glob("*.yaml"):
            try:
                content = file.read_text()
                parsed = parse_instinct_file(content)
                for instinct in parsed:
                    instinct["_source_file"] = str(file)
                    instinct["_source_type"] = directory.name
                instincts.extend(parsed)
            except Exception as error:
                print(f"Warning: Failed to parse {file}: {error}", file=sys.stderr)

    return instincts


def cmd_status(_args):
    instincts = load_all_instincts()

    if not instincts:
        print("No instincts found.")
        print("\nInstinct directories:")
        print(f"  Personal:  {PERSONAL_DIR}")
        print(f"  Inherited: {INHERITED_DIR}")
        return

    by_domain = defaultdict(list)
    for instinct in instincts:
        domain = instinct.get("domain", "general")
        by_domain[domain].append(instinct)

    print(f"\n{'=' * 60}")
    print(f"  INSTINCT STATUS - {len(instincts)} total")
    print(f"{'=' * 60}\n")

    personal = [instinct for instinct in instincts if instinct.get("_source_type") == "personal"]
    inherited = [instinct for instinct in instincts if instinct.get("_source_type") == "inherited"]
    print(f"  Personal:  {len(personal)}")
    print(f"  Inherited: {len(inherited)}")
    print()

    for domain in sorted(by_domain.keys()):
        domain_instincts = by_domain[domain]
        print(f"## {domain.upper()} ({len(domain_instincts)})")
        print()

        for instinct in sorted(domain_instincts, key=lambda item: -item.get("confidence", 0.5)):
            confidence = instinct.get("confidence", 0.5)
            conf_bar = "█" * int(confidence * 10) + "░" * (10 - int(confidence * 10))
            trigger = instinct.get("trigger", "unknown trigger")

            print(f"  {conf_bar} {int(confidence * 100):3d}%  {instinct.get('id', 'unnamed')}")
            print(f"            trigger: {trigger}")

            content = instinct.get("content", "")
            action_match = re.search(r"## Action\s*\n\s*(.+?)(?:\n\n|\n##|$)", content, re.DOTALL)
            if action_match:
                action = action_match.group(1).strip().split("\n")[0]
                suffix = "..." if len(action) > 60 else ""
                print(f"            action: {action[:60]}{suffix}")

            print()

    if OBSERVATIONS_FILE.exists():
        obs_count = sum(1 for _ in open(OBSERVATIONS_FILE))
        print("─────────────────────────────────────────────────────────")
        print(f"  Observations: {obs_count} events logged")
        print(f"  File: {OBSERVATIONS_FILE}")

    print(f"\n{'=' * 60}\n")


def cmd_import(args):
    source = args.source

    if source.startswith("http://") or source.startswith("https://"):
        print(f"Fetching from URL: {source}")
        try:
            with urllib.request.urlopen(source) as response:
                content = response.read().decode("utf-8")
        except Exception as error:
            print(f"Error fetching URL: {error}", file=sys.stderr)
            return 1
    else:
        path = Path(source).expanduser()
        if not path.exists():
            print(f"File not found: {path}", file=sys.stderr)
            return 1
        content = path.read_text()

    new_instincts = parse_instinct_file(content)
    if not new_instincts:
        print("No valid instincts found in source.")
        return 1

    print(f"\nFound {len(new_instincts)} instincts to import.\n")

    existing = load_all_instincts()
    existing_ids = {instinct.get("id") for instinct in existing}

    to_add = []
    duplicates = []
    to_update = []

    for instinct in new_instincts:
        instinct_id = instinct.get("id")
        if instinct_id in existing_ids:
            existing_instinct = next((item for item in existing if item.get("id") == instinct_id), None)
            if existing_instinct:
                if instinct.get("confidence", 0) > existing_instinct.get("confidence", 0):
                    to_update.append(instinct)
                else:
                    duplicates.append(instinct)
        else:
            to_add.append(instinct)

    min_conf = args.min_confidence or 0.0
    to_add = [instinct for instinct in to_add if instinct.get("confidence", 0.5) >= min_conf]
    to_update = [instinct for instinct in to_update if instinct.get("confidence", 0.5) >= min_conf]

    if to_add:
        print(f"NEW ({len(to_add)}):")
        for instinct in to_add:
            print(f"  + {instinct.get('id')} (confidence: {instinct.get('confidence', 0.5):.2f})")

    if to_update:
        print(f"\nUPDATE ({len(to_update)}):")
        for instinct in to_update:
            print(f"  ~ {instinct.get('id')} (confidence: {instinct.get('confidence', 0.5):.2f})")

    if duplicates:
        print(f"\nSKIP ({len(duplicates)} - already exists with equal/higher confidence):")
        for instinct in duplicates[:5]:
            print(f"  - {instinct.get('id')}")
        if len(duplicates) > 5:
            print(f"  ... and {len(duplicates) - 5} more")

    if args.dry_run:
        print("\n[DRY RUN] No changes made.")
        return 0

    if not to_add and not to_update:
        print("\nNothing to import.")
        return 0

    if not args.force:
        response = input(f"\nImport {len(to_add)} new, update {len(to_update)}? [y/N] ")
        if response.lower() != "y":
            print("Cancelled.")
            return 0

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    source_name = Path(source).stem if not source.startswith("http") else "web-import"
    output_file = INHERITED_DIR / f"{source_name}-{timestamp}.yaml"

    all_to_write = to_add + to_update
    output_content = f"# Imported from {source}\n# Date: {datetime.now().isoformat()}\n\n"

    for instinct in all_to_write:
        output_content += "---\n"
        output_content += f"id: {instinct.get('id')}\n"
        output_content += f"trigger: \"{instinct.get('trigger', 'unknown')}\"\n"
        output_content += f"confidence: {instinct.get('confidence', 0.5)}\n"
        output_content += f"domain: {instinct.get('domain', 'general')}\n"
        output_content += "source: inherited\n"
        output_content += f"imported_from: \"{source}\"\n"
        if instinct.get("source_repo"):
            output_content += f"source_repo: {instinct.get('source_repo')}\n"
        output_content += "---\n\n"
        output_content += instinct.get("content", "") + "\n\n"

    output_file.write_text(output_content)

    print("\n✅ Import complete!")
    print(f"   Added: {len(to_add)}")
    print(f"   Updated: {len(to_update)}")
    print(f"   Saved to: {output_file}")

    return 0


def cmd_export(args):
    instincts = load_all_instincts()

    if not instincts:
        print("No instincts to export.")
        return 1

    if args.domain:
        instincts = [instinct for instinct in instincts if instinct.get("domain") == args.domain]

    if args.min_confidence:
        instincts = [instinct for instinct in instincts if instinct.get("confidence", 0.5) >= args.min_confidence]

    if not instincts:
        print("No instincts match the criteria.")
        return 1

    output = f"# Instincts export\n# Date: {datetime.now().isoformat()}\n# Total: {len(instincts)}\n\n"

    for instinct in instincts:
        output += "---\n"
        for key in ["id", "trigger", "confidence", "domain", "source", "source_repo"]:
            if instinct.get(key):
                value = instinct[key]
                if key == "trigger":
                    output += f'{key}: "{value}"\n'
                else:
                    output += f"{key}: {value}\n"
        output += "---\n\n"
        output += instinct.get("content", "") + "\n\n"

    if args.output:
        Path(args.output).write_text(output)
        print(f"Exported {len(instincts)} instincts to {args.output}")
    else:
        print(output)

    return 0


def cmd_evolve(args):
    instincts = load_all_instincts()

    if len(instincts) < 3:
        print("Need at least 3 instincts to analyze patterns.")
        print(f"Currently have: {len(instincts)}")
        return 1

    print(f"\n{'=' * 60}")
    print(f"  EVOLVE ANALYSIS - {len(instincts)} instincts")
    print(f"{'=' * 60}\n")

    by_domain = defaultdict(list)
    for instinct in instincts:
        domain = instinct.get("domain", "general")
        by_domain[domain].append(instinct)

    high_conf = [instinct for instinct in instincts if instinct.get("confidence", 0) >= 0.8]
    print(f"High confidence instincts (>=80%): {len(high_conf)}")

    trigger_clusters = defaultdict(list)
    for instinct in instincts:
        trigger = instinct.get("trigger", "")
        trigger_key = trigger.lower()
        for keyword in ["when", "creating", "writing", "adding", "implementing", "testing"]:
            trigger_key = trigger_key.replace(keyword, "").strip()
        trigger_clusters[trigger_key].append(instinct)

    skill_candidates = []
    for trigger, cluster in trigger_clusters.items():
        if len(cluster) >= 2:
            avg_conf = sum(item.get("confidence", 0.5) for item in cluster) / len(cluster)
            skill_candidates.append({
                "trigger": trigger,
                "instincts": cluster,
                "avg_confidence": avg_conf,
                "domains": list({item.get("domain", "general") for item in cluster}),
            })

    skill_candidates.sort(key=lambda item: (-len(item["instincts"]), -item["avg_confidence"]))

    print(f"\nPotential skill clusters found: {len(skill_candidates)}")

    if skill_candidates:
        print("\n## SKILL CANDIDATES\n")
        for index, candidate in enumerate(skill_candidates[:5], 1):
            print(f"{index}. Cluster: \"{candidate['trigger']}\"")
            print(f"   Instincts: {len(candidate['instincts'])}")
            print(f"   Avg confidence: {candidate['avg_confidence']:.0%}")
            print(f"   Domains: {', '.join(candidate['domains'])}")
            print("   Instincts:")
            for instinct in candidate["instincts"][:3]:
                print(f"     - {instinct.get('id')}")
            print()

    workflow_instincts = [instinct for instinct in instincts if instinct.get("domain") == "workflow" and instinct.get("confidence", 0) >= 0.7]
    if workflow_instincts:
        print(f"\n## COMMAND CANDIDATES ({len(workflow_instincts)})\n")
        for instinct in workflow_instincts[:5]:
            trigger = instinct.get("trigger", "unknown")
            cmd_name = trigger.replace("when ", "").replace("implementing ", "").replace("a ", "")
            cmd_name = cmd_name.replace(" ", "-")[:20]
            print(f"  /{cmd_name}")
            print(f"    From: {instinct.get('id')}")
            print(f"    Confidence: {instinct.get('confidence', 0.5):.0%}")
            print()

    agent_candidates = [candidate for candidate in skill_candidates if len(candidate["instincts"]) >= 3 and candidate["avg_confidence"] >= 0.75]
    if agent_candidates:
        print(f"\n## AGENT CANDIDATES ({len(agent_candidates)})\n")
        for candidate in agent_candidates[:3]:
            agent_name = candidate["trigger"].replace(" ", "-")[:20] + "-agent"
            print(f"  {agent_name}")
            print(f"    Covers {len(candidate['instincts'])} instincts")
            print(f"    Avg confidence: {candidate['avg_confidence']:.0%}")
            print()

    if args.generate:
        print("\n[Would generate evolved structures here]")
        print("  Skills would be saved to:", EVOLVED_DIR / "skills")
        print("  Commands would be saved to:", EVOLVED_DIR / "commands")
        print("  Agents would be saved to:", EVOLVED_DIR / "agents")

    print(f"\n{'=' * 60}\n")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Instinct CLI for Continuous Learning v2")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("status", help="Show instinct status")

    import_parser = subparsers.add_parser("import", help="Import instincts")
    import_parser.add_argument("source", help="File path or URL")
    import_parser.add_argument("--dry-run", action="store_true", help="Preview without importing")
    import_parser.add_argument("--force", action="store_true", help="Skip confirmation")
    import_parser.add_argument("--min-confidence", type=float, help="Minimum confidence threshold")

    export_parser = subparsers.add_parser("export", help="Export instincts")
    export_parser.add_argument("--output", "-o", help="Output file")
    export_parser.add_argument("--domain", help="Filter by domain")
    export_parser.add_argument("--min-confidence", type=float, help="Minimum confidence")

    evolve_parser = subparsers.add_parser("evolve", help="Analyze and evolve instincts")
    evolve_parser.add_argument("--generate", action="store_true", help="Generate evolved structures")

    args = parser.parse_args()

    if args.command == "status":
        return cmd_status(args)
    if args.command == "import":
        return cmd_import(args)
    if args.command == "export":
        return cmd_export(args)
    if args.command == "evolve":
        return cmd_evolve(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
