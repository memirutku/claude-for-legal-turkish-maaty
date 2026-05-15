"""In-memory skill registry — loaded once at startup, queried per request."""
from __future__ import annotations

import logging
from pathlib import Path

from legal_plugins.skill_loader import Skill, discover_skills

logger = logging.getLogger(__name__)


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}

    def load(self, plugins_dir: Path) -> None:
        """Discover all skills under plugins_dir and index by skill_id."""
        self._skills.clear()
        for skill in discover_skills(plugins_dir):
            if skill.skill_id in self._skills:
                logger.warning("Duplicate skill_id %r — keeping first occurrence", skill.skill_id)
                continue
            self._skills[skill.skill_id] = skill
        logger.info("Loaded %d skills from %s", len(self._skills), plugins_dir)

    def get(self, skill_id: str) -> Skill | None:
        return self._skills.get(skill_id)

    def list_all(self) -> list[Skill]:
        return list(self._skills.values())

    def count(self) -> int:
        return len(self._skills)

    def categories(self) -> dict[str, list[Skill]]:
        grouped: dict[str, list[Skill]] = {}
        for skill in self._skills.values():
            grouped.setdefault(skill.category, []).append(skill)
        return grouped


registry = SkillRegistry()
