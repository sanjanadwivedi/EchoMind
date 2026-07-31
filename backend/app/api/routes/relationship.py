import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.npc import NPC
from app.models.personality import Personality
from app.models.relationship import Relationship

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/relationships", tags=["Relationships"])


@router.get("/{npc_id}/{player_id}")
def get_relationship_info(
    npc_id: UUID,
    player_id: UUID,
    db: Session = Depends(get_db),
):
    npc = db.query(NPC).filter(NPC.id == npc_id).first()
    if npc is None:
        raise HTTPException(status_code=404, detail="NPC not found")

    personality = (
        db.query(Personality)
        .filter(Personality.npc_id == npc_id)
        .first()
    )

    relationship = (
        db.query(Relationship)
        .filter(
            Relationship.npc_id == npc_id,
            Relationship.player_id == player_id,
        )
        .first()
    )

    result: dict[str, Any] = {
        "npc": {
            "id": str(npc.id),
            "name": npc.name,
            "role": npc.role,
            "location": npc.location,
        },
        "personality": None,
        "relationship": None,
    }

    if personality:
        result["personality"] = {
            "trust": personality.trust,
            "respect": personality.respect,
            "warmth": personality.warmth,
            "curiosity": personality.curiosity,
            "fear": personality.fear,
            "loyalty": personality.loyalty,
            "aggression": personality.aggression,
        }

    if relationship:
        result["relationship"] = {
            "affinity": relationship.affinity,
            "trust": relationship.trust,
        }

    return result
