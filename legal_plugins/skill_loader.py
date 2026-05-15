"""SKILL.md parser — extracts YAML frontmatter + markdown instructions."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import yaml


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


@dataclass
class Skill:
    skill_id: str
    name: str
    description: str
    argument_hint: str
    category: str
    plugin: str
    instructions: str
    references: list[str] = field(default_factory=list)
    raw_path: str = ""
    model_hint: str | None = None

    def public_metadata(self) -> dict:
        """Return JSON-safe metadata for /skills catalog (without instructions)."""
        return {
            "id": self.skill_id,
            "name": self.name,
            "description": self.description,
            "argument_hint": self.argument_hint,
            "category": self.category,
            "plugin": self.plugin,
            "model_hint": self.model_hint,
        }


def parse_skill_file(skill_md_path: Path) -> Skill | None:
    """Parse one SKILL.md file. Returns None if frontmatter is malformed."""
    try:
        content = skill_md_path.read_text(encoding="utf-8")
    except Exception:
        return None

    match = FRONTMATTER_RE.match(content)
    if not match:
        return None

    frontmatter_raw, body = match.groups()
    try:
        meta = yaml.safe_load(frontmatter_raw) or {}
    except yaml.YAMLError:
        return None

    # Derive skill_id from path: plugins/<plugin>/skills/<skill>/SKILL.md
    parts = skill_md_path.parts
    try:
        plugin = parts[-4]      # e.g. "privacy-legal"
        skill_dir = parts[-2]   # e.g. "pia-generation"
    except IndexError:
        return None

    skill_id = skill_dir  # Use directory name as canonical id
    name = meta.get("name", skill_dir)
    description = (meta.get("description") or "").strip()
    argument_hint = meta.get("argument-hint", "").strip()
    category = plugin.replace("-legal", "")
    model_hint = meta.get("model")

    # Optional references/ siblings
    references: list[str] = []
    refs_dir = skill_md_path.parent / "references"
    if refs_dir.is_dir():
        references = sorted(p.name for p in refs_dir.iterdir() if p.is_file())

    return Skill(
        skill_id=skill_id,
        name=name,
        description=description,
        argument_hint=argument_hint,
        category=category,
        plugin=plugin,
        instructions=body.strip(),
        references=references,
        raw_path=str(skill_md_path),
        model_hint=model_hint,
    )


def discover_skills(plugins_dir: Path) -> Iterable[Skill]:
    """Walk plugins_dir for SKILL.md files. Yields parsed Skill objects."""
    if not plugins_dir.is_dir():
        return
    for skill_md in plugins_dir.glob("*/skills/*/SKILL.md"):
        skill = parse_skill_file(skill_md)
        if skill is not None:
            yield skill
