import json
import logging
from uuid import UUID

from app.ai.memory.memory_extractor import MemoryExtractor
from app.services.memory.memory_service import MemoryService

logger = logging.getLogger(__name__)


class ConversationService:

    def __init__(self, db):
        self.memory_extractor = MemoryExtractor()
        self.memory_service = MemoryService(db)

    def process_conversation(
        self,
        npc_id: UUID,
        player_id: UUID,
        conversation: str,
    ):
        logger.info("Processing conversation for memory extraction")
        logger.debug("Conversation text: %s", conversation)

        memory = self.memory_extractor.extract(conversation)

        logger.debug("Extracted memory: %s", json.dumps(memory, indent=2))

        if not memory.get("should_store", False):
            logger.debug("Memory skipped (should_store=false)")
            return None

        logger.info("Creating memory: category=%s", memory.get("category"))

        created = self.memory_service.create_memory(
            npc_id=npc_id,
            player_id=player_id,
            summary=memory["summary"],
            category=memory["category"],
            event_type=memory["event_type"],
            emotion=memory["emotion"],
            importance=memory["importance"],
            confidence=memory["confidence"],
        )

        if created is None:
            logger.info("Memory skipped (duplicate detected)")
            return None

        logger.info("Memory created: %s", created.id)

        return created