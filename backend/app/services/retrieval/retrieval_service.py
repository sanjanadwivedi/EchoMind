from typing import Any, Dict, List, Optional
from uuid import UUID

from app.ai.embeddings.embedding_service import EmbeddingService
from app.ai.retrieval.bm25_retriever import BM25Retriever
from app.repositories.memory import MemoryRepository


class RetrievalService:
    """Hybrid Memory Retrieval Service combining Dense Vector Embeddings and Sparse BM25 Search
    via Reciprocal Rank Fusion (RRF).
    """

    def __init__(self, db):
        self.embedding_service = EmbeddingService()
        self.memory_repo = MemoryRepository(db)
        self.bm25_retriever = BM25Retriever()

    def reciprocal_rank_fusion(
        self,
        dense_results: List[Dict[str, Any]],
        sparse_results: List[Dict[str, Any]],
        k: int = 60,
    ) -> List[Dict[str, Any]]:
        """Combines dense vector search ranks and sparse BM25 ranks using RRF score formula:
        RRF_Score(d) = sum(1 / (k + rank(d)))
        """
        rrf_scores: Dict[str, float] = {}
        memory_map: Dict[str, Dict[str, Any]] = {}

        # 1. Process dense vector ranks
        for rank, item in enumerate(dense_results, start=1):
            mem_id = str(getattr(item["memory"], "id", id(item["memory"])))
            memory_map[mem_id] = item
            rrf_scores[mem_id] = rrf_scores.get(mem_id, 0.0) + (1.0 / (k + rank))

        # 2. Process sparse BM25 ranks
        for rank, item in enumerate(sparse_results, start=1):
            mem_id = str(getattr(item["memory"], "id", id(item["memory"])))
            if mem_id not in memory_map:
                memory_map[mem_id] = item
            rrf_scores[mem_id] = rrf_scores.get(mem_id, 0.0) + (1.0 / (k + rank))

        # 3. Build fused result list sorted by RRF score descending
        fused = []
        for mem_id, rrf_score in rrf_scores.items():
            base_item = memory_map[mem_id]
            fused_item = dict(base_item)
            fused_item["rrf_score"] = round(rrf_score, 6)
            fused.append(fused_item)

        fused.sort(key=lambda x: x["rrf_score"], reverse=True)
        return fused

    def retrieve_memories(
        self,
        npc_id: UUID,
        player_id: UUID,
        query: str,
        top_k: int = 5,
        categories: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        # ---------------------------------
        # Step 1: Semantic (Dense Vector) retrieval
        # ---------------------------------
        chroma_results = self.embedding_service.search(
            query=query,
            npc_id=npc_id,
            player_id=player_id,
            top_k=max(top_k * 3, 20),   # retrieve more candidates for reranking
        )

        if not chroma_results or not chroma_results.get("ids"):
            return []

        ids = chroma_results.get("ids", [[]])[0]

        if not ids:
            return []

        memory_map = self.memory_repo.get_memories_by_ids(
            [UUID(memory_id) for memory_id in ids]
        )

        distances = chroma_results.get("distances", [[]])[0] if chroma_results.get("distances") else []

        dense_retrieved = []

        for memory_id, distance in zip(ids, distances):
            memory = memory_map.get(memory_id)
            if not memory:
                continue

            dense_retrieved.append(
                {
                    "memory": memory,
                    "distance": distance,
                }
            )

        if not dense_retrieved:
            return []

        # ---------------------------------
        # Step 2: Sparse (BM25 Keyword) retrieval
        # ---------------------------------
        sparse_retrieved = self.bm25_retriever.rank(query=query, documents=dense_retrieved)

        # ---------------------------------
        # Step 3: Reciprocal Rank Fusion (RRF)
        # ---------------------------------
        fused_memories = self.reciprocal_rank_fusion(
            dense_results=dense_retrieved,
            sparse_results=sparse_retrieved,
            k=60,
        )

        # ---------------------------------
        # Step 4: Category filtering
        # ---------------------------------
        if categories:
            filtered = [
                item
                for item in fused_memories
                if item["memory"].category in categories
            ]

            if filtered:
                return filtered[:top_k]

        # ---------------------------------
        # Fallback to top_k fused items
        # ---------------------------------
        return fused_memories[:top_k]