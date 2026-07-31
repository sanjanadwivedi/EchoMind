from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.player import Player
from app.models.npc import NPC
from app.models.personality import Personality
from app.models.relationship import Relationship


def seed_database():
    db: Session = SessionLocal()

    try:
        # --------------------------
        # Player
        # --------------------------
        player = db.query(Player).filter_by(username="Sanjana").first()

        if player is None:
            player = Player(username="Sanjana")
            db.add(player)
            db.commit()
            db.refresh(player)

        # --------------------------
        # NPCs
        # --------------------------
        npc_data = [
            {
                "name": "Eldon",
                "role": "Merchant",
                "location": "Marketplace",
                "personality": {
                    "trust": 60,
                    "respect": 55,
                    "warmth": 90,
                    "curiosity": 75,
                    "fear": 10,
                    "loyalty": 70,
                    "aggression": 5,
                },
            },
            {
                "name": "Ragnar",
                "role": "Guard",
                "location": "Castle Gate",
                "personality": {
                    "trust": 45,
                    "respect": 85,
                    "warmth": 20,
                    "curiosity": 35,
                    "fear": 5,
                    "loyalty": 95,
                    "aggression": 70,
                },
            },
            {
                "name": "Luna",
                "role": "Scholar",
                "location": "Library",
                "personality": {
                    "trust": 70,
                    "respect": 80,
                    "warmth": 60,
                    "curiosity": 95,
                    "fear": 15,
                    "loyalty": 50,
                    "aggression": 10,
                },
            },
        ]

        for item in npc_data:

            npc = db.query(NPC).filter_by(name=item["name"]).first()

            if npc is None:
                npc = NPC(
                    name=item["name"],
                    role=item["role"],
                    location=item["location"],
                )

                db.add(npc)
                db.commit()
                db.refresh(npc)

            personality = (
                db.query(Personality)
                .filter_by(npc_id=npc.id)
                .first()
            )

            if personality is None:
                personality = Personality(
                    npc_id=npc.id,
                    **item["personality"],
                )

                db.add(personality)

            relationship = (
                db.query(Relationship)
                .filter_by(
                    npc_id=npc.id,
                    player_id=player.id,
                )
                .first()
            )

            if relationship is None:
                relationship = Relationship(
                    npc_id=npc.id,
                    player_id=player.id,
                    affinity=0.6,
                    trust=0.7,
                )

                db.add(relationship)

        db.commit()

        print("\nDatabase seeded successfully!")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()