from chromadb import PersistentClient

from app.core.config import settings

# Chroma will store vectors locally in this directory
client = PersistentClient(path=settings.CHROMA_DB_PATH)

# Collection for all memories
memory_collection = client.get_or_create_collection(
    name="npc_memories"
)