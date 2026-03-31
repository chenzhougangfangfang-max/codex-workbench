#!/usr/bin/env python3
import argparse
import re
from pathlib import Path


SYSTEM_ROOT = Path("/home/chengang/.codex/skills/.system")
USER_ROOT = Path("/home/chengang/.codex/skills")
AGENTS_ROOT = Path("/home/chengang/.agents/skills")


def has_skill_md(path: Path) -> bool:
    return (path / "SKILL.md").is_file()


def list_dirs(root: Path):
    if not root.exists() or not root.is_dir():
        return []
    return sorted([p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")], key=lambda p: p.name)


def collect_system_skills():
    return [p for p in list_dirs(SYSTEM_ROOT) if has_skill_md(p)]


def collect_user_skills():
    return [p for p in list_dirs(USER_ROOT) if has_skill_md(p)]


def collect_agent_linked_skills():
    skills = []
    for entry in list_dirs(AGENTS_ROOT):
        if entry.is_symlink():
            target = entry.resolve()
            for child in list_dirs(target):
                if has_skill_md(child):
                    skills.append((entry.name, child))
    return skills


def print_section(title: str, items):
    print(title)
    if not items:
        print("- (none)")
        print()
        return
    for item in items:
        print(f"- {item}")
    print()


def list_skills(args) -> int:
    system_skills = [p.name for p in collect_system_skills()]
    user_skills = [p.name for p in collect_user_skills()]
    agent_skills = [f"{source}:{skill.name}" for source, skill in collect_agent_linked_skills()]

    if args.flat:
        for name in system_skills + user_skills + agent_skills:
            print(name)
        return 0

    print_section("System Skills", system_skills)
    print_section("User Skills", user_skills)
    print_section("Agent-linked Skills", agent_skills)
    return 0


def parse_frontmatter(text: str):
    if not text.startswith("---\n"):
        return None, "SKILL.md must start with YAML frontmatter"
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        return None, "SKILL.md frontmatter is not closed with ---"
    return parts[0][4:], None


def extract_key(frontmatter: str, key: str):
    pattern = re.compile(rf"(?m)^{re.escape(key)}:\s*(.+?)\s*$")
    match = pattern.search(frontmatter)
    if not match:
        return None
    value = match.group(1).strip()
    if value.startswith(("'", '"')) and value.endswith(("'", '"')) and len(value) >= 2:
        value = value[1:-1]
    return value.strip()


def collect_skill_result(root: Path):
    errors = []
    warnings = []
    oks = []

    if not root.exists():
        errors.append(f"skill directory not found: {root}")
        return {"path": str(root), "ok": oks, "warn": warnings, "error": errors}
    if not root.is_dir():
        errors.append(f"path is not a directory: {root}")
        return {"path": str(root), "ok": oks, "warn": warnings, "error": errors}

    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        errors.append("missing SKILL.md at skill root")
    else:
        oks.append("SKILL.md exists")
        text = skill_md.read_text(encoding="utf-8")
        frontmatter, frontmatter_error = parse_frontmatter(text)
        if frontmatter_error:
            errors.append(frontmatter_error)
        else:
            oks.append("frontmatter detected")
            name = extract_key(frontmatter, "name")
            description = extract_key(frontmatter, "description")
            if not name:
                errors.append("frontmatter missing required name")
            else:
                oks.append(f"name: {name}")
                if name != root.name:
                    warnings.append(f"frontmatter name '{name}' differs from directory name '{root.name}'")
                if not re.fullmatch(r"[a-z0-9-]{1,63}", name):
                    warnings.append("name should usually use lowercase letters, digits, and hyphens only")
            if not description:
                errors.append("frontmatter missing required description")
            else:
                oks.append("description present")

    for folder in ("agents", "scripts", "references", "assets"):
        p = root / folder
        if p.exists():
            if p.is_dir():
                oks.append(f"optional folder present: {folder}/")
            else:
                warnings.append(f"{folder} exists but is not a directory")

    readme = root / "README.md"
    if readme.exists():
        warnings.append("README.md found; most skills should keep guidance inside SKILL.md or bundled references")

    return {
        "path": str(root),
        "ok": oks,
        "warn": warnings,
        "error": errors,
    }


def print_skill_result(result: dict) -> int:
    for line in result["ok"]:
        print(f"OK: {line}")
    for line in result["warn"]:
        print(f"WARN: {line}")
    for line in result["error"]:
        print(f"ERROR: {line}")
    return 1 if result["error"] else 0


def write_report(path: Path, results: list[dict]) -> None:
    lines = ["# Skill Vetter Report", ""]
    for result in results:
        status = "FAIL" if result["error"] else "PASS"
        lines.append(f"## {result['path']}")
        lines.append("")
        lines.append(f"- Status: `{status}`")
        lines.append(f"- OK: `{len(result['ok'])}`")
        lines.append(f"- Warnings: `{len(result['warn'])}`")
        lines.append(f"- Errors: `{len(result['error'])}`")
        lines.append("")
        if result["ok"]:
            lines.append("### OK")
            lines.append("")
            for item in result["ok"]:
                lines.append(f"- {item}")
            lines.append("")
        if result["warn"]:
            lines.append("### Warnings")
            lines.append("")
            for item in result["warn"]:
                lines.append(f"- {item}")
            lines.append("")
        if result["error"]:
            lines.append("### Errors")
            lines.append("")
            for item in result["error"]:
                lines.append(f"- {item}")
            lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def iter_skills(root: Path):
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        if child.name.startswith("."):
            continue
        yield child


def vet_skill(args) -> int:
    root = Path(args.path).expanduser().resolve()
    if not args.batch:
        result = collect_skill_result(root)
        exit_code = print_skill_result(result)
        if args.report:
            write_report(Path(args.report).expanduser().resolve(), [result])
        return exit_code

    if not root.exists():
        print(f"ERROR: directory not found: {root}")
        return 1
    if not root.is_dir():
        print(f"ERROR: path is not a directory: {root}")
        return 1

    any_failures = False
    checked = 0
    results = []
    for skill_dir in iter_skills(root):
        checked += 1
        print(f"== {skill_dir} ==")
        result = collect_skill_result(skill_dir)
        results.append(result)
        exit_code = print_skill_result(result)
        if exit_code != 0:
            any_failures = True
        print()

    if checked == 0:
        print(f"WARN: no skill directories found under {root}")
        return 0

    if args.report:
        write_report(Path(args.report).expanduser().resolve(), results)

    return 1 if any_failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Unified toolbox entrypoint for local Codex utilities.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list-skills", help="List installed Codex skills on this machine.")
    list_parser.add_argument("--flat", action="store_true", help="Print a flat list without sections.")
    list_parser.set_defaults(func=list_skills)

    vet_parser = subparsers.add_parser("vet-skill", help="Validate Codex skill folders.")
    vet_parser.add_argument("path", help="Path to a skill directory or a parent directory containing skill folders.")
    vet_parser.add_argument("--batch", action="store_true", help="Treat path as a directory containing many skill folders.")
    vet_parser.add_argument("--report", help="Write a Markdown report to this file path.")
    vet_parser.set_defaults(func=vet_skill)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
