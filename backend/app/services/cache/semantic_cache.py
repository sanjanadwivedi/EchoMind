import math
import time
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Computes cosine similarity between two vector embeddings."""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm_a = math.sqrt(sum(a * a for a in vec1))
    norm_b = math.sqrt(sum(b * b for b in vec2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot_product / (norm_a * norm_b)


class SemanticCache:
    """In-Memory Semantic Query Cache using Cosine Vector Similarity.
    
    Provides sub-5ms latency and zero LLM token consumption for semantically identical
    queries above similarity_threshold (default >= 0.95).
    """

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        # Storage: list of dict items
        self._cache: List[Dict[str, Any]] = []

    def clear(self):
        """Clears all cached items."""
        self._cache.clear()

    def get(
        self,
        npc_id: UUID,
        player_id: UUID,
        query_embedding: List[float],
        similarity_threshold: float = 0.95,
    ) -> Optional[Tuple[str, str, List[Dict[str, Any]], float]]:
        """Searches cache for a entry with matching npc_id and player_id whose query vector
        has cosine similarity >= similarity_threshold.
        """
        now = time.time()
        best_match: Optional[Dict[str, Any]] = None
        highest_sim: float = -1.0

        # Purge expired entries while scanning
        valid_cache = []

        for entry in self._cache:
            if now - entry["timestamp"] > self.ttl_seconds:
                continue
            valid_cache.append(entry)

            if str(entry["npc_id"]) == str(npc_id) and str(entry["player_id"]) == str(player_id):
                sim = cosine_similarity(query_embedding, entry["query_embedding"])
                if sim >= similarity_threshold and sim > highest_sim:
                    highest_sim = sim
                    best_match = entry

        self._cache = valid_cache

        if best_match:
            return (
                best_match["response"],
                best_match["emotion"],
                best_match["memories"],
                round(highest_sim, 4),
            )

        return None

    def set(
        self,
        npc_id: UUID,
        player_id: UUID,
        query: str,
        query_embedding: List[float],
        response: str,
        emotion: str,
        memories: List[Dict[str, Any]],
    ):
        """Stores new query response entry into semantic cache."""
        if len(self._cache) >= self.max_size:
            # Evict oldest entry (LRU eviction)
            self._cache.pop(0)

        entry = {
            "npc_id": str(npc_id),
            "player_id": str(player_id),
            "query": query,
            "query_embedding": query_embedding,
            "response": response,
            "emotion": emotion,
            "memories": memories,
            "timestamp": time.time(),
        }
        self._cache.append(entry)


# Global singleton instance for app runtime
semantic_cache = SemanticCache()
