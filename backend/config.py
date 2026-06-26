import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Google AI
    google_api_key: str
    google_cloud_project: str
    google_application_credentials: str
    documentai_processor_id: str
    documentai_location: str = "us"

    # Neo4j
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection_name: str = "paper_brain_chunks"
    qdrant_vector_size: int = 768  # text-embedding-004 output dimension

    # App
    environment: str = "development"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    # Ensure GOOGLE_APPLICATION_CREDENTIALS is set as env var for Google SDKs
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.google_application_credentials
    os.environ["GOOGLE_CLOUD_PROJECT"] = settings.google_cloud_project
    return settings
