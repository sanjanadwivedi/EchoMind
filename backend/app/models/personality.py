import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Personality(Base, TimestampMixin):
    __tablename__ = "personalities"

    __table_args__ = (
        CheckConstraint("trust BETWEEN 0 AND 100"),
        CheckConstraint("respect BETWEEN 0 AND 100"),
        CheckConstraint("warmth BETWEEN 0 AND 100"),
        CheckConstraint("curiosity BETWEEN 0 AND 100"),
        CheckConstraint("fear BETWEEN 0 AND 100"),
        CheckConstraint("loyalty BETWEEN 0 AND 100"),
        CheckConstraint("aggression BETWEEN 0 AND 100"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    npc_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("npcs.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    trust: Mapped[int] = mapped_column(Integer, default=50)
    respect: Mapped[int] = mapped_column(Integer, default=50)
    warmth: Mapped[int] = mapped_column(Integer, default=50)
    curiosity: Mapped[int] = mapped_column(Integer, default=50)
    fear: Mapped[int] = mapped_column(Integer, default=10)
    loyalty: Mapped[int] = mapped_column(Integer, default=50)
    aggression: Mapped[int] = mapped_column(Integer, default=20)

    npc = relationship("NPC", back_populates="personality")