from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.npc import NPC
from app.models.personality import Personality
from app.models.player import Player
from app.models.relationship import Relationship
from app.schemas.npc import NPCCreate, NPCResponse

router = APIRouter(prefix="/npcs", tags=["NPCs"])


@router.get("/", response_model=list[NPCResponse])
def get_npcs(db: Session = Depends(get_db)):
    npcs = db.query(NPC).all()

    return [
        NPCResponse(
            id=str(npc.id),
            name=npc.name,
            role=npc.role,
            location=npc.location,
        )
        for npc in npcs
    ]


@router.post("/", response_model=NPCResponse, status_code=status.HTTP_201_CREATED)
def create_npc(payload: NPCCreate, db: Session = Depends(get_db)):
    # Guard against duplicate NPC names
    existing = db.query(NPC).filter(NPC.name == payload.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An NPC named '{payload.name}' already exists.",
        )

    # Create NPC
    npc = NPC(
        name=payload.name,
        role=payload.role,
        location=payload.location,
    )
    db.add(npc)
    db.commit()
    db.refresh(npc)

    # Create Personality
    p_data = payload.personality.model_dump() if payload.personality else {}
    personality = Personality(npc_id=npc.id, **p_data)
    db.add(personality)

    # Create Relationship for existing players
    players = db.query(Player).all()
    for player in players:
        rel = Relationship(
            npc_id=npc.id,
            player_id=player.id,
            affinity=0.5,
            trust=0.5,
        )
        db.add(rel)

    db.commit()

    return NPCResponse(
        id=str(npc.id),
        name=npc.name,
        role=npc.role,
        location=npc.location,
    )



@router.get("/{npc_id}", response_model=NPCResponse)
def get_npc(npc_id: UUID, db: Session = Depends(get_db)):
    npc = db.query(NPC).filter(NPC.id == npc_id).first()

    if npc is None:
        raise HTTPException(status_code=404, detail="NPC not found")

    return NPCResponse(
        id=str(npc.id),
        name=npc.name,
        role=npc.role,
        location=npc.location,
    )