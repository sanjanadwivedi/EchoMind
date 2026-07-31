import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.relationship import Relationship

logger = logging.getLogger(__name__)


class RelationshipService:

    def __init__(self, db: Session):
        self.db = db

    def get_relationship(
        self,
        npc_id: UUID,
        player_id: UUID,
    ):
        relationship = (
            self.db.query(Relationship)
            .filter(
                Relationship.npc_id == npc_id,
                Relationship.player_id == player_id,
            )
            .first()
        )

        if relationship is None:
            raise ValueError(
                f"Relationship not found for NPC {npc_id} "
                f"and player {player_id}"
            )

        return relationship

    def relationship_prompt(
        self,
        npc_id: UUID,
        player_id: UUID,
    ):
        r = self.get_relationship(
            npc_id,
            player_id,
        )

        return f"""
Relationship

Trust: {r.trust}

Affinity: {r.affinity}
"""