from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.neo4j_client import init_driver, close_driver, get_driver
from database.qdrant_client import init_qdrant, get_qdrant_client, close_qdrant
from config import get_settings
from routers import ingest, query, graph, seed
from models.schemas import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    await init_driver()
    await init_qdrant()
    print(f"[Paper Brain] All services initialized. Environment: {settings.environment}")
    yield
    await close_driver()
    await close_qdrant()
    print("[Paper Brain] Shutdown complete.")


app = FastAPI(
    title="Paper Brain API",
    description="Industrial Knowledge Intelligence Platform — GraphRAG + Neo4j + Qdrant + Gemini",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router)
app.include_router(query.router)
app.include_router(graph.router)
app.include_router(seed.router)


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    neo4j_ok = False
    qdrant_ok = False
    gemini_ok = False

    try:
        driver = await get_driver()
        async with driver.session() as session:
            await session.run("RETURN 1")
        neo4j_ok = True
    except Exception:
        pass

    try:
        client = await get_qdrant_client()
        await client.get_collections()
        qdrant_ok = True
    except Exception:
        pass

    try:
        settings = get_settings()
        gemini_ok = bool(settings.google_api_key)
    except Exception:
        pass

    status = "healthy" if all([neo4j_ok, qdrant_ok, gemini_ok]) else "degraded"

    return HealthResponse(
        status=status,
        neo4j=neo4j_ok,
        qdrant=qdrant_ok,
        gemini=gemini_ok,
        timestamp=datetime.now(timezone.utc).isoformat()
    )
