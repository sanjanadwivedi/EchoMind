import logging
from uuid import UUID

from openai import OpenAI

from app.ai.embeddings.chroma_client import memory_collection
from app.core.config import settings

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)


class EmbeddingService:

    def generate_embedding(self, text: str) -> list[float]:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )

        return response.data[0].embedding

    def get_embedding(self, text: str) -> list[float]:
        """Alias for generate_embedding for API consistency."""
        return self.generate_embedding(text)

    def store_memory(
        self,
        memory_id: UUID,
        text: str,
        metadata: dict,
    ):
        embedding = self.generate_embedding(text)

        memory_collection.add(
            ids=[str(memory_id)],
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata],
        )

    def search(
        self,
        query: str,
        npc_id: UUID,
        player_id: UUID,
        top_k: int = 5,
    ):
        embedding = self.generate_embedding(query)

        return memory_collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            where={
                "$and": [
                    {"npc_id": str(npc_id)},
                    {"player_id": str(player_id)},
                ]
            },
        )