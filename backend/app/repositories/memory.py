from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.memory import Memory
from app.repositories.base import BaseRepository


class MemoryRepository(BaseRepository[Memory]):
    def __init__(self, db: Session):
        super().__init__(db, Memory)

    def get_recent_memories(
        self,
        npc_id: UUID,
        player_id: UUID,
        limit: int = 20,
    ):
        result = self.db.execute(
            select(Memory)
            .where(
                Memory.npc_id == npc_id,
                Memory.player_id == player_id,
            )
            .order_by(desc(Memory.created_at))
            .limit(limit)
        )

        return result.scalars().all()

    def get_memories_by_ids(self, memory_ids: list[UUID]):
        if not memory_ids:
            return {}

        result = self.db.execute(
            select(Memory).where(
                Memory.id.in_(memory_ids)
            )
        )

        memories = result.scalars().all()

        return {
            str(memory.id): memory
            for memory in memories
        }

    def increment_recall_count(self, memory: Memory):
        memory.recall_count += 1
        self.db.commit()
        self.db.refresh(memory)
        return memory

    def update_importance(
        self,
        memory: Memory,
        importance: float,
    ):
        memory.importance = importance
        self.db.commit()
        self.db.refresh(memory)
        return memory

    # ⭐ NEW
    def update_state(
        self,
        memory: Memory,
        state: str,
    ):
        memory.state = state
        self.db.commit()
        self.db.refresh(memory)
        return memory

    def archive_memory(self, memory: Memory):
        memory.state = "ARCHIVED"
        self.db.commit()
        self.db.refresh(memory)
        return memory
    
    def get_memories_by_categories(
        self,
        npc_id: UUID,
        player_id: UUID,
        categories: list[str],
    ):
        """
        Returns all memories that belong to one of the requested categories.
        """

        if not categories:
            return []

        result = self.db.execute(
            select(Memory)
            .where(
                Memory.npc_id == npc_id,
                Memory.player_id == player_id,
                Memory.category.in_(categories),
            )
            .order_by(desc(Memory.created_at))
        )

        return result.scalars().all()