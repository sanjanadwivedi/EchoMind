from unittest.mock import MagicMock
import pytest

from app.ai.retrieval.bm25_retriever import BM25Retriever
from app.services.retrieval.retrieval_service import RetrievalService


@pytest.fixture
def bm25_retriever():
    return BM25Retriever()


def test_bm25_exact_keyword_matching(bm25_retriever):
    mem1 = MagicMock(summary="Player ordered a mithril broadsword")
    mem2 = MagicMock(summary="Player enjoys drinking dark espresso in the morning")
    mem3 = MagicMock(summary="Player owns a rare magical amulet")

    docs = [
        {"memory": mem1, "distance": 0.3},
        {"memory": mem2, "distance": 0.1},
        {"memory": mem3, "distance": 0.4},
    ]

    # Query specifically targeting "mithril broadsword"
    ranked = bm25_retriever.rank("mithril broadsword", docs)
    assert ranked[0]["memory"].summary == "Player ordered a mithril broadsword"
    assert ranked[0]["bm25_score"] > 0.0


def test_reciprocal_rank_fusion():
    service = RetrievalService(db=MagicMock())
    mem_a = MagicMock(id="id-a", category="preference", summary="Player loves espresso")
    mem_b = MagicMock(id="id-b", category="event", summary="Player bought a broadsword")

    dense = [{"memory": mem_a}, {"memory": mem_b}]
    sparse = [{"memory": mem_b}, {"memory": mem_a}]

    fused = service.reciprocal_rank_fusion(dense, sparse, k=60)
    assert len(fused) == 2
    assert "rrf_score" in fused[0]
    # Since rank positions were swapped, RRF score for both should be identical: 1/61 + 1/62
    assert fused[0]["rrf_score"] == fused[1]["rrf_score"]
