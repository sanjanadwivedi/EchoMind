import uuid
from datetime import datetime

from sqlalchemy import Float, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import MemoryCategory


class Memory(Base, TimestampMixin):
    __tablename__ = "memories"

    __table_args__ = (
        Index("idx_memory_npc", "npc_id"),
        Index("idx_memory_player", "player_id"),
        Index("idx_memory_importance", "importance"),
        Index("idx_memory_state", "state"),
        Index("idx_memory_category", "category"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    npc_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("npcs.id", ondelete="CASCADE"),
        nullable=False,
    )

    player_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Memory classification
    event_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String(30),
        default=MemoryCategory.OTHER.value,
        nullable=False,
    )

    emotion: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    state: Mapped[str] = mapped_column(
        String(20),
        default="SHORT_TERM",
        nullable=False,
    )

    importance: Mapped[float] = mapped_column(
        Float,
        default=0.5,
        nullable=False,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
    )

    recall_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    last_recalled_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    embedding_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    context: Mapped[dict] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )


    npc = relationship(
        "NPC",
        back_populates="memories",
    )

    player = relationship(
        "Player",
        back_populates="memories",
    )