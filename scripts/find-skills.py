#!/usr/bin/env python3
import argparse
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


def main() -> int:
    parser = argparse.ArgumentParser(description="List installed Codex skills on this machine.")
    parser.add_argument("--flat", action="store_true", help="Print a flat list without sections.")
    args = parser.parse_args()

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


if __name__ == "__main__":
    raise SystemExit(main())
