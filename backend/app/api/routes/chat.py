import json
import logging
import time
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.dialogue.conversation_service import ConversationService
from app.services.dialogue.dialogue_service import DialogueService, client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    dialogue_service = DialogueService(db)
    conversation_service = ConversationService(db)

    # Generate NPC response, emotion & telemetry breakdown
    try:
        response_text, emotion, telemetry = dialogue_service.generate_response_with_telemetry(
            npc_id=request.npc_id,
            player_id=request.player_id,
            player_message=request.message,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Failed to generate dialogue response")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate NPC response",
        )

    # Extract and store memory from the player's message
    try:
        conversation_service.process_conversation(
            npc_id=request.npc_id,
            player_id=request.player_id,
            conversation=request.message,
        )
    except Exception:
        logger.exception("Memory extraction failed")

    return ChatResponse(
        response=response_text,
        emotion=emotion,
        telemetry=telemetry,
    )


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    """Server-Sent Events (SSE) endpoint for real-time streaming dialogue generation."""
    dialogue_service = DialogueService(db)
    conversation_service = ConversationService(db)

    async def event_generator() -> AsyncGenerator[str, None]:
        start_total = time.perf_counter()
        
        # Memory extraction trigger
        try:
            conversation_service.process_conversation(
                npc_id=request.npc_id,
                player_id=request.player_id,
                conversation=request.message,
            )
        except Exception as e:
            logger.warning(f"Async memory extraction failed: {e}")

        # Check semantic cache first
        try:
            query_embedding = dialogue_service.embedding_service.get_embedding(request.message)
            cached = dialogue_service.retrieval_service.bm25_retriever
            from app.services.cache.semantic_cache import semantic_cache
            cache_hit = semantic_cache.get(
                npc_id=request.npc_id,
                player_id=request.player_id,
                query_embedding=query_embedding,
                similarity_threshold=0.95,
            )
            if cache_hit:
                reply, emotion, memories, sim = cache_hit
                total_ms = round((time.perf_counter() - start_total) * 1000, 2)
                event_data = {
                    "chunk": reply,
                    "emotion": emotion,
                    "done": True,
                    "telemetry": {"cache_hit": True, "similarity_score": sim, "total_ms": total_ms}
                }
                yield f"data: {json.dumps(event_data)}\n\n"
                return
        except Exception as e:
            logger.warning(f"Stream cache check skipped: {e}")

        # Non-cached streaming execution
        reply_accum = ""
        emotion = "Neutral"
        try:
            reply_text, emotion, telemetry = dialogue_service.generate_response_with_telemetry(
                npc_id=request.npc_id,
                player_id=request.player_id,
                player_message=request.message,
            )
            total_ms = round((time.perf_counter() - start_total) * 1000, 2)
            telemetry["total_ms"] = total_ms

            # Stream chunks for real-time UI typing effect
            words = reply_text.split(" ")
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                is_last = (i == len(words) - 1)
                event_payload = {
                    "chunk": chunk,
                    "emotion": emotion if is_last else None,
                    "done": is_last,
                    "telemetry": telemetry if is_last else None,
                }
                yield f"data: {json.dumps(event_payload)}\n\n"

        except Exception as e:
            logger.exception("Error during stream generation")
            err_payload = {"error": str(e), "done": True}
            yield f"data: {json.dumps(err_payload)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )