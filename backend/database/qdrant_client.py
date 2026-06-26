from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams
from config import get_settings

_client: AsyncQdrantClient | None = None


async def init_qdrant() -> AsyncQdrantClient:
    global _client
    settings = get_settings()
    _client = AsyncQdrantClient(
        host=settings.qdrant_host,
        port=settings.qdrant_port
    )
    await _ensure_collection(_client, settings)
    return _client


async def _ensure_collection(client: AsyncQdrantClient, settings) -> None:
    exists = await client.collection_exists(settings.qdrant_collection_name)
    if not exists:
        await client.create_collection(
            collection_name=settings.qdrant_collection_name,
            vectors_config=VectorParams(
                size=settings.qdrant_vector_size,
                distance=Distance.COSINE
            )
        )


async def get_qdrant_client() -> AsyncQdrantClient:
    return _client


async def close_qdrant() -> None:
    if _client:
        await _client.close()
