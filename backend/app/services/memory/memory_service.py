import logging
from uuid import UUID

from app.ai.embeddings.embedding_service import EmbeddingService
from app.models.enums import MemoryCategory
from app.repositories.memory import MemoryRepository

logger = logging.getLogger(__name__)


class MemoryService:

    DUPLICATE_DISTANCE_THRESHOLD = 0.15

    def __init__(self, db):
        self.memory_repo = MemoryRepository(db)
        self.embedding_service = EmbeddingService()

    def create_memory(
        self,
        npc_id: UUID,
        player_id: UUID,
        summary: str,
        category: str,
        event_type: str,
        emotion: str,
        importance: float,
        confidence: float,
        location: str | None = None,
    ):

        # -----------------------------
        # Validate category
        # -----------------------------
        valid_categories = {item.value for item in MemoryCategory}

        if category not in valid_categories:
            logger.warning(
                "Invalid category '%s', falling back to '%s'",
                category,
                MemoryCategory.OTHER.value,
            )
            category = MemoryCategory.OTHER.value

        # -----------------------------
        # Duplicate detection
        # -----------------------------
        try:
            results = self.embedding_service.search(
                query=summary,
                npc_id=npc_id,
                player_id=player_id,
                top_k=3,
            )
        except Exception:
            logger.exception("ChromaDB search failed during duplicate check")
            results = None

        if results:
            ids = results.get("ids") or [[]]
            docs = results.get("documents") or [[]]
            distances = results.get("distances") or [[]]

            if (
                len(ids) > 0
                and len(ids[0]) > 0
                and len(distances) > 0
                and len(distances[0]) > 0
            ):

                for doc_id, doc, distance in zip(
                    ids[0],
                    docs[0],
                    distances[0],
                ):
                    logger.debug(
                        "Duplicate candidate: id=%s, distance=%.6f, text=%s",
                        doc_id,
                        distance,
                        doc,
                    )

                    if distance < self.DUPLICATE_DISTANCE_THRESHOLD:
                        logger.info(
                            "Duplicate memory detected (distance=%.6f)",
                            distance,
                        )
                        return None

        # -----------------------------
        # Save memory
        # -----------------------------
        memory = self.memory_repo.create(
            npc_id=npc_id,
            player_id=player_id,
            summary=summary,
            category=category,
            event_type=event_type,
            emotion=emotion,
            state="SHORT_TERM",
            importance=importance,
            confidence=confidence,
            location=location,
            embedding_id="",
            context={},
        )

        # -----------------------------
        # Store embedding
        # -----------------------------
        try:
            self.embedding_service.store_memory(
                memory_id=memory.id,
                text=summary,
                metadata={
                    "npc_id": str(npc_id),
                    "player_id": str(player_id),
                    "category": category,
                    "emotion": emotion,
                    "importance": importance,
                },
            )
        except Exception:
            logger.exception(
                "Failed to store embedding for memory %s", memory.id
            )
            # Memory is still saved in PostgreSQL even if embedding fails

        memory.embedding_id = str(memory.id)

        self.memory_repo.db.commit()
        self.memory_repo.db.refresh(memory)

        logger.info("Memory stored successfully: %s", memory.id)

        return memory