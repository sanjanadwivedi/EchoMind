import uuid

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"

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

    player_message: Mapped[str] = mapped_column(Text)

    npc_response: Mapped[str] = mapped_column(Text)

    npc = relationship("NPC", back_populates="conversations")
    player = relationship("Player", back_populates="conversations")