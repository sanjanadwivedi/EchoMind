from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.player import Player
from app.schemas.player import PlayerCreate, PlayerResponse

router = APIRouter(prefix="/players", tags=["Players"])


@router.get("/", response_model=list[PlayerResponse])
def get_players(db: Session = Depends(get_db)):
    players = db.query(Player).all()

    if not players:
        default_player = Player(username="Sanjana")
        db.add(default_player)
        db.commit()
        db.refresh(default_player)
        players = [default_player]

    return [
        PlayerResponse(
            id=str(player.id),
            username=player.username,
        )
        for player in players
    ]


@router.get("/{player_id}", response_model=PlayerResponse)
def get_player(player_id: UUID, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.id == player_id).first()

    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    return PlayerResponse(
        id=str(player.id),
        username=player.username,
    )


@router.post("/", response_model=PlayerResponse, status_code=201)
def create_player(
    request: PlayerCreate,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(Player)
        .filter(Player.username == request.username)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Player with this username already exists",
        )

    player = Player(username=request.username)
    db.add(player)
    db.commit()
    db.refresh(player)

    return PlayerResponse(
        id=str(player.id),
        username=player.username,
    )