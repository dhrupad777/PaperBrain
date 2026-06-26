from neo4j import AsyncGraphDatabase, AsyncDriver
from config import get_settings

_driver: AsyncDriver | None = None


async def init_driver() -> AsyncDriver:
    global _driver
    settings = get_settings()
    _driver = AsyncGraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password)
    )
    await _create_constraints(_driver)
    return _driver


async def _create_constraints(driver: AsyncDriver) -> None:
    statements = [
        "CREATE CONSTRAINT asset_tag_unique IF NOT EXISTS FOR (a:Asset) REQUIRE a.tag_number IS UNIQUE",
        "CREATE CONSTRAINT facility_id_unique IF NOT EXISTS FOR (f:Facility) REQUIRE f.id IS UNIQUE",
        "CREATE CONSTRAINT area_id_unique IF NOT EXISTS FOR (a:FunctionalArea) REQUIRE a.id IS UNIQUE",
        "CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS FOR (c:DocumentChunk) REQUIRE c.id IS UNIQUE",
        "CREATE CONSTRAINT obs_id_unique IF NOT EXISTS FOR (o:KnowledgeObservation) REQUIRE o.id IS UNIQUE",
        "CREATE INDEX asset_id_index IF NOT EXISTS FOR (a:Asset) ON (a.id)",
    ]
    async with driver.session() as session:
        for stmt in statements:
            await session.run(stmt)


async def get_driver() -> AsyncDriver:
    return _driver


async def close_driver() -> None:
    if _driver:
        await _driver.close()
