import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai.embeddings.chroma_client import memory_collection
from app.db.session import get_db
from app.repositories.memory import MemoryRepository
from app.schemas.memory import MemoryResponse, ReflectionResponse
from app.services.reflection.memory_reflection_service import (
    MemoryReflectionService,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/memory",
    tags=["Memory"],
)


@router.delete("/{memory_id}")
def delete_memory(
    memory_id: UUID,
    db: Session = Depends(get_db),
):
    repo = MemoryRepository(db)
    memory = repo.get(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")

    if memory.embedding_id:
        try:
            memory_collection.delete(ids=[memory.embedding_id])
        except Exception as e:
            logger.warning(f"Could not delete ChromaDB embedding {memory.embedding_id}: {e}")

    repo.delete(memory_id)
    return {"status": "deleted", "id": str(memory_id)}



@router.post("/reflect", response_model=ReflectionResponse)
def reflect(
    npc_id: UUID,
    player_id: UUID,
    db: Session = Depends(get_db),
):
    repo = MemoryRepository(db)

    memories = repo.get_recent_memories(
        npc_id=npc_id,
        player_id=player_id,
        limit=10,
    )

    if not memories:
        raise HTTPException(
            status_code=404,
            detail="No memories found for this NPC-player pair",
        )

    service = MemoryReflectionService()

    try:
        summary = service.reflect(memories)
    except Exception:
        logger.exception("Reflection failed")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate reflection",
        )

    return ReflectionResponse(
        memory_count=len(memories),
        input_memories=[memory.summary for memory in memories],
        reflection=summary,
    )


@router.get("/debug", response_model=list[MemoryResponse])
def debug_memories(
    npc_id: UUID,
    player_id: UUID,
    db: Session = Depends(get_db),
):
    repo = MemoryRepository(db)

    memories = repo.get_recent_memories(
        npc_id=npc_id,
        player_id=player_id,
        limit=100,
    )

    return [
        MemoryResponse(
            id=str(memory.id),
            summary=memory.summary,
            category=memory.category,
            state=memory.state,
            importance=memory.importance,
            confidence=memory.confidence,
            recall_count=memory.recall_count,
            last_recalled_at=memory.last_recalled_at,
            created_at=memory.created_at,
            event_type=memory.event_type,
            emotion=memory.emotion,
            location=memory.location,
            embedding_id=memory.embedding_id,
            context=memory.context,
        )
        for memory in memories
    ]