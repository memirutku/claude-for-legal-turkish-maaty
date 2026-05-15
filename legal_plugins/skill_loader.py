"""SKILL.md parser — extracts YAML frontmatter + markdown instructions.

v0.1.1: also reads the plugin's CLAUDE.md profile (Türk hukuku kuralları)
and exposes it via ``Skill.plugin_profile`` so the runtime prepends it
to the system prompt — recommended by Said Sürücü's "Claude for Legal —
Türk Hukuku Uygulanabilirlik Raporu" (2026-05-13).
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import yaml


logger = logging.getLogger(__name__)

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)

# Plugin CLAUDE.md template'lerinde üstte yorum bloğu var (Claude Code'a özgü
# davranış yönlendirmesi). LLM sistem promptuna girmesin diye stripped.
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


@dataclass
class Skill:
    skill_id: str
    name: str
    description: str
    argument_hint: str
    category: str
    plugin: str
    instructions: str
    plugin_profile: str = ""  # CLAUDE.md from plugin root (Türk hukuku kuralları)
    references: list[str] = field(default_factory=list)
    raw_path: str = ""
    model_hint: str | None = None

    def system_prompt(self) -> str:
        """Build the full system prompt: plugin profile + skill instructions.

        Plugin CLAUDE.md (Türk hukuku kuralları, KVKK/TBK/TTK template'i)
        skill instructions'ından ÖNCE gelir. Bu, Said Sürücü'nün
        uygulanabilirlik raporundaki "manuel profil zorunlu" tavsiyesini
        otomatize eder — kullanıcının CLAUDE.md profilini elle doldurma
        gereksinimini service-level'da minimal düzeyde ele alır.

        [PLACEHOLDER] içeren satırlar template'te kalır; LLM bu placeholder'ları
        görürse spesifik soru sorabilir veya generic davranır. İleride
        kullanıcı kurum profili özelliği eklendiğinde, bu noktada
        substitusyon yapılabilir.
        """
        if not self.plugin_profile:
            return self.instructions
        return (
            f"{self.plugin_profile}\n\n"
            "---\n\n"
            f"{self.instructions}"
        )

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
            "has_plugin_profile": bool(self.plugin_profile),
        }


def _load_plugin_profile(plugin_root: Path) -> str:
    """Load and clean the plugin's CLAUDE.md profile.

    Strips the HTML comment block at the top (which contains Claude Code-
    specific routing instructions not relevant for our service runtime).
    [PLACEHOLDER] markers are left intact — see Skill.system_prompt() note.
    Returns empty string if CLAUDE.md is absent or unreadable.
    """
    claude_md = plugin_root / "CLAUDE.md"
    if not claude_md.is_file():
        return ""
    try:
        raw = claude_md.read_text(encoding="utf-8")
    except Exception as exc:
        logger.warning("CLAUDE.md read failed for %s: %s", plugin_root.name, exc)
        return ""
    cleaned = HTML_COMMENT_RE.sub("", raw).strip()
    return cleaned


def _fallback_metadata(skill_md_path: Path, content: str) -> dict:
    """Salvage minimum metadata when YAML frontmatter parse fails.

    Tries line-by-line regex for ``key: value`` style entries in the first
    20 lines (between ``---`` markers if present). Logs the salvage attempt
    so operators can see which skills had malformed frontmatter.
    """
    head = content.split("---", 2)
    block = head[1] if len(head) >= 2 else "\n".join(content.splitlines()[:20])
    meta: dict = {}
    for line in block.splitlines():
        m = re.match(r"^([a-zA-Z][\w-]*)\s*:\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if val.startswith('"') and val.endswith('"'):
            val = val[1:-1]
        meta.setdefault(key, val)
    logger.warning(
        "Frontmatter YAML parse failed for %s — salvaged keys: %s",
        skill_md_path, sorted(meta.keys()),
    )
    return meta


def parse_skill_file(skill_md_path: Path, plugin_profile: str = "") -> Skill | None:
    """Parse one SKILL.md file. Returns None only if path can't be read."""
    try:
        content = skill_md_path.read_text(encoding="utf-8")
    except Exception as exc:
        logger.warning("SKILL.md read failed for %s: %s", skill_md_path, exc)
        return None

    match = FRONTMATTER_RE.match(content)
    if match:
        frontmatter_raw, body = match.groups()
        try:
            meta = yaml.safe_load(frontmatter_raw) or {}
        except yaml.YAMLError:
            # Fallback parser — keeps skill usable even with malformed YAML
            meta = _fallback_metadata(skill_md_path, content)
    else:
        # No frontmatter — treat entire file as body, no metadata
        logger.warning("No YAML frontmatter in %s — using filename as id", skill_md_path)
        meta = {}
        body = content

    # Derive skill_id from path: plugins/<plugin>/skills/<skill>/SKILL.md
    parts = skill_md_path.parts
    try:
        plugin = parts[-4]      # e.g. "privacy-legal"
        skill_dir = parts[-2]   # e.g. "pia-generation"
    except IndexError:
        logger.warning("Unexpected path shape for %s — skipping", skill_md_path)
        return None

    skill_id = skill_dir  # Use directory name as canonical id
    name = meta.get("name") or skill_dir
    description = (meta.get("description") or "").strip()
    argument_hint = (meta.get("argument-hint") or "").strip()
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
        plugin_profile=plugin_profile,
        references=references,
        raw_path=str(skill_md_path),
        model_hint=model_hint,
    )


def discover_skills(plugins_dir: Path) -> Iterable[Skill]:
    """Walk plugins_dir for SKILL.md files. Yields parsed Skill objects.

    Plugin CLAUDE.md profiles are loaded once per plugin (cached) and
    attached to each Skill in that plugin.
    """
    if not plugins_dir.is_dir():
        return
    profile_cache: dict[str, str] = {}
    for skill_md in plugins_dir.glob("*/skills/*/SKILL.md"):
        plugin_name = skill_md.parts[-4]
        if plugin_name not in profile_cache:
            profile_cache[plugin_name] = _load_plugin_profile(skill_md.parent.parent.parent)
        skill = parse_skill_file(skill_md, plugin_profile=profile_cache[plugin_name])
        if skill is not None:
            yield skill
