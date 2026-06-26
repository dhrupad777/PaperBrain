from langchain_google_vertexai import VertexAIEmbeddings
from config import get_settings

_embeddings: VertexAIEmbeddings | None = None


def _get_embeddings() -> VertexAIEmbeddings:
    global _embeddings
    if _embeddings is None:
        settings = get_settings()  # also sets GOOGLE_APPLICATION_CREDENTIALS env var
        _embeddings = VertexAIEmbeddings(
            model_name="text-embedding-004",
            project=settings.google_cloud_project
        )
    return _embeddings


async def embed_text(text: str) -> list[float]:
    embeddings = _get_embeddings()
    return await embeddings.aembed_query(text)


async def embed_texts(texts: list[str]) -> list[list[float]]:
    embeddings = _get_embeddings()
    return await embeddings.aembed_documents(texts)
