import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Player(Base, TimestampMixin):
    __tablename__ = "players"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    username: Mapped[str] = mapped_column(
        unique=True,
        index=True,
        nullable=False,
    )

    relationships = relationship(
        "Relationship",
        back_populates="player",
        cascade="all, delete-orphan",
    )

    memories = relationship(
        "Memory",
        back_populates="player",
        cascade="all, delete-orphan",
    )

    conversations = relationship(
        "Conversation",
        back_populates="player",
        cascade="all, delete-orphan",
    )