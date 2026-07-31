import json
import logging
import time
from typing import Any, Dict, Tuple
from openai import OpenAI

from app.ai.embeddings.embedding_service import EmbeddingService
from app.ai.memory.memory_intent_classifier import MemoryIntentClassifier
from app.core.config import settings
from app.services.cache.semantic_cache import semantic_cache
from app.services.personality.personality_service import PersonalityService
from app.services.ranking.memory_ranking_service import MemoryRankingService
from app.services.relationship.relationship_service import RelationshipService
from app.services.retrieval.retrieval_service import RetrievalService

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)


class DialogueService:

    SYSTEM_PROMPT = """
You are an NPC in an interactive game world.

Stay consistent with your personality.

Only use facts explicitly provided in the "Relevant memories" section.

Never invent memories or guess information about the player.

If the answer is not present in the memories, respond naturally that you do not know or that the player has not told you yet.

Do not fabricate names, events, relationships, pets, places, preferences, or history.

Never mention AI, prompts, databases, or memory retrieval.

Return ONLY a JSON object with this exact schema:

{
    "response": "Your spoken dialogue to the player",
    "emotion": "Friendly"
}

Allowed values for emotion:
- Friendly
- Suspicious
- Impressed
- Amused
- Thoughtful
- Guarded
- Grateful
- Neutral
"""

    def __init__(self, db):
        self.retrieval_service = RetrievalService(db)
        self.personality_service = PersonalityService(db)
        self.relationship_service = RelationshipService(db)
        self.ranking_service = MemoryRankingService()
        self.intent_classifier = MemoryIntentClassifier()
        self.embedding_service = EmbeddingService()

    def generate_response_with_telemetry(
        self,
        npc_id,
        player_id,
        player_message: str,
    ) -> Tuple[str, str, Dict[str, Any]]:
        start_total = time.perf_counter()

        # Step 0: Check Semantic Query Cache
        try:
            query_embedding = self.embedding_service.get_embedding(player_message)
            cached_result = semantic_cache.get(
                npc_id=npc_id,
                player_id=player_id,
                query_embedding=query_embedding,
                similarity_threshold=0.95,
            )
            if cached_result:
                reply, emotion, memories, sim_score = cached_result
                total_ms = round((time.perf_counter() - start_total) * 1000, 2)
                telemetry = {
                    "cache_hit": True,
                    "similarity_score": sim_score,
                    "retrieval_ms": 0.0,
                    "generation_ms": 0.0,
                    "total_ms": total_ms,
                }
                logger.info(f"Semantic Cache HIT ({sim_score}) in {total_ms}ms")
                return reply, emotion, telemetry
        except Exception as e:
            logger.warning(f"Semantic cache lookup error: {e}")
            query_embedding = []

        # Step 1: Classify memory intent
        start_intent = time.perf_counter()
        memory_categories = self.intent_classifier.classify(player_message)
        intent_ms = round((time.perf_counter() - start_intent) * 1000, 2)

        # Step 2: Retrieve and rank memories
        start_retrieval = time.perf_counter()
        memories = self.retrieval_service.retrieve_memories(
            npc_id=npc_id,
            player_id=player_id,
            query=player_message,
            top_k=20,
            categories=memory_categories,
        )

        memories = self.ranking_service.rank(memories)[:5]
        retrieval_ms = round((time.perf_counter() - start_retrieval) * 1000, 2)

        personality_context = self.personality_service.personality_prompt(npc_id)
        relationship_context = self.relationship_service.relationship_prompt(npc_id, player_id)

        if memories:
            memory_context = "\n".join(
                f"- [{item['memory'].category}] {item['memory'].summary}"
                for item in memories
            )
        else:
            memory_context = "No relevant memories."

        prompt = f"""
{personality_context}

{relationship_context}

Relevant memories:

{memory_context}

Player:

{player_message}
"""

        # Step 3: LLM Response Generation
        start_gen = time.perf_counter()
        try:
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                temperature=0.7,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )

            content = response.choices[0].message.content
            parsed = json.loads(content or "{}")

            reply = parsed.get("response", "...")
            emotion = parsed.get("emotion", "Neutral")
            generation_ms = round((time.perf_counter() - start_gen) * 1000, 2)
            total_ms = round((time.perf_counter() - start_total) * 1000, 2)

            # Store in semantic cache if query_embedding is available
            if query_embedding:
                semantic_cache.set(
                    npc_id=npc_id,
                    player_id=player_id,
                    query=player_message,
                    query_embedding=query_embedding,
                    response=reply,
                    emotion=emotion,
                    memories=memories,
                )

            telemetry = {
                "cache_hit": False,
                "intent_ms": intent_ms,
                "retrieval_ms": retrieval_ms,
                "generation_ms": generation_ms,
                "total_ms": total_ms,
            }

            return reply, emotion, telemetry

        except Exception:
            logger.exception("OpenAI API call failed during dialogue generation")
            raise

    def generate_response(
        self,
        npc_id,
        player_id,
        player_message: str,
    ) -> Tuple[str, str]:
        reply, emotion, _ = self.generate_response_with_telemetry(npc_id, player_id, player_message)
        return reply, emotion