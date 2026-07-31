import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.personality import Personality

logger = logging.getLogger(__name__)


class PersonalityService:

    def __init__(self, db: Session):
        self.db = db

    def get_personality(self, npc_id: UUID):

        personality = (
            self.db.query(Personality)
            .filter(Personality.npc_id == npc_id)
            .first()
        )

        if personality is None:
            raise ValueError(
                f"Personality not found for NPC {npc_id}"
            )

        return personality

    def personality_prompt(self, npc_id: UUID):

        p = self.get_personality(npc_id)

        return f"""
NPC Personality

Trust: {p.trust}
Respect: {p.respect}
Warmth: {p.warmth}
Curiosity: {p.curiosity}
Fear: {p.fear}
Loyalty: {p.loyalty}
Aggression: {p.aggression}
"""