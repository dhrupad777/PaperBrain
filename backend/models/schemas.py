from pydantic import BaseModel, Field
from typing import Optional


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=2000)


class SeedRequest(BaseModel):
    force_reload: bool = False


class QueryResponse(BaseModel):
    answer: str
    route_taken: str
    sources: list[str]
    latency_ms: float


class IngestDocumentResponse(BaseModel):
    filename: str
    chunks_stored: int
    assets_linked: int
    message: str


class IngestVoiceResponse(BaseModel):
    observation_id: str
    transcript: str
    asset_linked: Optional[str]
    extracted: dict
    message: str


class AssetNode(BaseModel):
    tag_number: str
    model_number: Optional[str] = None
    manufacturer: Optional[str] = None
    base_emissions_co2_ppm: Optional[float] = None


class AssetNeighbor(BaseModel):
    tag_number: str
    direction: str


class AssetGraphResponse(BaseModel):
    asset: AssetNode
    connections: list[AssetNeighbor]
    observations: list[str]
    document_sources: list[str]


class SeedResponse(BaseModel):
    assets_created: int
    relationships_created: int
    message: str


class HealthResponse(BaseModel):
    status: str
    neo4j: bool
    qdrant: bool
    gemini: bool
    timestamp: str
