from uuid import uuid4
import pytest

from app.services.cache.semantic_cache import SemanticCache, cosine_similarity


def test_cosine_similarity_identical():
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    assert cosine_similarity(v1, v2) == 1.0


def test_cosine_similarity_orthogonal():
    v1 = [1.0, 0.0, 0.0]
    v2 = [0.0, 1.0, 0.0]
    assert cosine_similarity(v1, v2) == 0.0


def test_semantic_cache_hit_and_miss():
    cache = SemanticCache(max_size=10, ttl_seconds=3600)
    npc_id = uuid4()
    player_id = uuid4()

    q_vec1 = [0.1, 0.2, 0.8, 0.5]
    # Very similar vector (cosine sim > 0.99)
    q_vec2 = [0.101, 0.201, 0.801, 0.501]
    # Completely different vector
    q_vec_diff = [0.9, -0.2, 0.1, 0.0]

    cache.set(
        npc_id=npc_id,
        player_id=player_id,
        query="What drink do I like?",
        query_embedding=q_vec1,
        response="You like strong espresso.",
        emotion="Friendly",
        memories=[],
    )

    # 1. Test hit for similar query
    hit = cache.get(npc_id=npc_id, player_id=player_id, query_embedding=q_vec2, similarity_threshold=0.95)
    assert hit is not None
    response, emotion, memories, sim_score = hit
    assert response == "You like strong espresso."
    assert sim_score >= 0.95

    # 2. Test miss for different query
    miss = cache.get(npc_id=npc_id, player_id=player_id, query_embedding=q_vec_diff, similarity_threshold=0.95)
    assert miss is None
