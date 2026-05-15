"""Skill catalog routes — list metadata for UI consumption."""
from fastapi import APIRouter, HTTPException

from legal_plugins.skill_registry import registry

router = APIRouter()


@router.get("/skills")
async def list_skills() -> dict:
    """Return all registered skills as metadata list (no instructions)."""
    return {
        "skills": [s.public_metadata() for s in registry.list_all()],
        "by_category": {
            cat: [s.public_metadata() for s in skills]
            for cat, skills in registry.categories().items()
        },
    }


@router.get("/skills/{skill_id}")
async def get_skill(skill_id: str) -> dict:
    """Return one skill's full metadata + instructions length (not full body)."""
    skill = registry.get(skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail=f"Skill {skill_id!r} not found")
    meta = skill.public_metadata()
    meta["instructions_chars"] = len(skill.instructions)
    meta["references"] = skill.references
    return meta
