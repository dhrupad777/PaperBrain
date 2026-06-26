import time
from fastapi import APIRouter
from pipelines.graphrag_pipeline import run_query
from models.schemas import QueryRequest, QueryResponse

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
async def query_knowledge_base(request: QueryRequest):
    start = time.time()
    result = await run_query(request.question)
    latency_ms = (time.time() - start) * 1000

    return QueryResponse(
        answer=result["answer"],
        route_taken=result["route_taken"],
        sources=result["sources"],
        latency_ms=round(latency_ms, 2)
    )
