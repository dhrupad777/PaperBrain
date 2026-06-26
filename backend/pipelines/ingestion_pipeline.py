import uuid
from qdrant_client.models import PointStruct
from services.documentai_service import extract_text_from_pdf
from services.embedding_service import embed_texts
from database.neo4j_client import get_driver
from database.qdrant_client import get_qdrant_client
from config import get_settings


async def ingest_document(
    pdf_bytes: bytes,
    filename: str,
    asset_tag: str | None = None
) -> dict:
    chunks = await extract_text_from_pdf(pdf_bytes, filename)
    if not chunks:
        return {"chunks_stored": 0, "assets_linked": 0, "filename": filename}

    chunk_texts = [c["chunk_text"] for c in chunks]
    vectors = await embed_texts(chunk_texts)

    settings = get_settings()
    client = await get_qdrant_client()

    points = []
    chunk_ids = []
    for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
        chunk_id = str(uuid.uuid4())
        chunk_ids.append(chunk_id)
        points.append(PointStruct(
            id=chunk_id,
            vector=vector,
            payload={
                "chunk_text": chunk["chunk_text"],
                "source_file": chunk["source_file"],
                "page_number": chunk["page_number"],
                "asset_tag": asset_tag,
                "chunk_index": i
            }
        ))

    await client.upsert(
        collection_name=settings.qdrant_collection_name,
        points=points
    )

    assets_linked = 0
    driver = await get_driver()
    async with driver.session() as session:
        for chunk, chunk_id in zip(chunks, chunk_ids):
            await session.run(
                """
                CREATE (dc:DocumentChunk {
                    id: $id,
                    source_file: $source_file,
                    page_number: $page_number,
                    chunk_text: $chunk_text
                })
                """,
                id=chunk_id,
                source_file=chunk["source_file"],
                page_number=chunk["page_number"],
                chunk_text=chunk["chunk_text"][:500]
            )
            if asset_tag:
                result = await session.run(
                    """
                    MATCH (a:Asset {tag_number: $tag})
                    MATCH (dc:DocumentChunk {id: $chunk_id})
                    MERGE (a)-[:DOCUMENTED_BY]->(dc)
                    RETURN a.tag_number
                    """,
                    tag=asset_tag,
                    chunk_id=chunk_id
                )
                record = await result.single()
                if record:
                    assets_linked += 1

    return {
        "chunks_stored": len(points),
        "assets_linked": assets_linked,
        "filename": filename
    }
