from fastapi import APIRouter, HTTPException
from database.neo4j_client import get_driver
from models.schemas import AssetGraphResponse, AssetNode, AssetNeighbor

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/asset/{tag_number}", response_model=AssetGraphResponse)
async def get_asset_graph(tag_number: str):
    driver = await get_driver()

    async with driver.session() as session:
        result = await session.run(
            """
            MATCH (a:Asset {tag_number: $tag})
            OPTIONAL MATCH (a)-[r:CONNECTED_TO]-(b:Asset)
            OPTIONAL MATCH (a)-[:HAS_OBSERVATION]->(o:KnowledgeObservation)
            OPTIONAL MATCH (a)-[:DOCUMENTED_BY]->(dc:DocumentChunk)
            RETURN a,
                   collect(DISTINCT {tag_number: b.tag_number, direction: r.direction}) as connections,
                   collect(DISTINCT o.observed_issue) as observations,
                   collect(DISTINCT dc.source_file) as doc_sources
            """,
            tag=tag_number
        )
        record = await result.single()

    if not record or record["a"] is None:
        raise HTTPException(status_code=404, detail=f"Asset '{tag_number}' not found")

    asset_data = dict(record["a"])
    connections = [
        AssetNeighbor(tag_number=c["tag_number"], direction=c["direction"] or "")
        for c in record["connections"]
        if c["tag_number"] is not None
    ]

    return AssetGraphResponse(
        asset=AssetNode(
            tag_number=asset_data.get("tag_number"),
            model_number=asset_data.get("model_number"),
            manufacturer=asset_data.get("manufacturer"),
            base_emissions_co2_ppm=asset_data.get("base_emissions_co2_ppm")
        ),
        connections=connections,
        observations=[o for o in record["observations"] if o],
        document_sources=list(set(s for s in record["doc_sources"] if s))
    )
