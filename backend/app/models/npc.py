import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class NPC(Base, TimestampMixin):
    __tablename__ = "npcs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(nullable=False)

    role: Mapped[str] = mapped_column(nullable=False)

    location: Mapped[str] = mapped_column(nullable=False)

    personality = relationship(
        "Personality",
        uselist=False,
        back_populates="npc",
        cascade="all, delete-orphan",
    )

    relationships = relationship(
        "Relationship",
        back_populates="npc",
        cascade="all, delete-orphan",
    )

    memories = relationship(
        "Memory",
        back_populates="npc",
        cascade="all, delete-orphan",
    )

    conversations = relationship(
        "Conversation",
        back_populates="npc",
        cascade="all, delete-orphan",
    )