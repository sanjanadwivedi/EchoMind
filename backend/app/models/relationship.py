import uuid

from sqlalchemy import ForeignKey, Float, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Relationship(Base, TimestampMixin):
    __tablename__ = "relationships"

    __table_args__ = (
        UniqueConstraint("npc_id", "player_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    npc_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("npcs.id", ondelete="CASCADE")
    )

    player_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE")
    )

    affinity: Mapped[float] = mapped_column(Float, default=0.0)
    trust: Mapped[float] = mapped_column(Float, default=0.5)

    npc = relationship("NPC", back_populates="relationships")
    player = relationship("Player", back_populates="relationships")