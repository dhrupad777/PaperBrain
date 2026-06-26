import os
import pandas as pd
from fastapi import APIRouter
from database.neo4j_client import get_driver
from models.schemas import SeedResponse, SeedRequest

router = APIRouter(prefix="/seed", tags=["seed"])

_SEED_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "seed")
)


@router.post("", response_model=SeedResponse)
async def load_seed_data(request: SeedRequest = SeedRequest()):
    assets_df = pd.read_csv(os.path.join(_SEED_PATH, "assets_seed.csv"))
    topology_df = pd.read_csv(os.path.join(_SEED_PATH, "topology_seed.csv"))

    driver = await get_driver()
    assets_created = 0
    relationships_created = 0

    async with driver.session() as session:
        # Root facility
        await session.run(
            "MERGE (f:Facility {id: 'FAC-DEFAULT'}) ON CREATE SET f.name = 'Main Plant', f.location = 'India'"
        )

        # Functional areas
        for area in assets_df["functional_area"].unique():
            area_id = f"AREA-{area.upper().replace('-', '_')}"
            await session.run(
                """
                MERGE (a:FunctionalArea {id: $area_id})
                ON CREATE SET a.name = $area_name
                WITH a
                MATCH (f:Facility {id: 'FAC-DEFAULT'})
                MERGE (f)-[:HAS_AREA]->(a)
                """,
                area_id=area_id,
                area_name=area
            )

        # Assets
        for _, row in assets_df.iterrows():
            area_id = f"AREA-{row['functional_area'].upper().replace('-', '_')}"
            result = await session.run(
                """
                MERGE (asset:Asset {tag_number: $tag_number})
                ON CREATE SET
                    asset.id = $id,
                    asset.model_number = $model_number,
                    asset.manufacturer = $manufacturer,
                    asset.base_emissions_co2_ppm = $base_emissions
                ON MATCH SET
                    asset.id = $id,
                    asset.model_number = $model_number,
                    asset.manufacturer = $manufacturer
                WITH asset
                MATCH (area:FunctionalArea {id: $area_id})
                MERGE (area)-[:HAS_ASSET]->(asset)
                RETURN asset.tag_number
                """,
                tag_number=row["tag_number"],
                id=row["id"],
                model_number=row["model_number"],
                manufacturer=row["manufacturer"],
                base_emissions=float(row["base_emissions_co2_ppm"]) if pd.notna(row.get("base_emissions_co2_ppm")) else 0.0,
                area_id=area_id
            )
            record = await result.single()
            if record:
                assets_created += 1

        # Topology relationships — topology CSV uses asset `id` column (e.g. PUMP-101)
        for _, row in topology_df.iterrows():
            result = await session.run(
                """
                MATCH (source:Asset {id: $source_id})
                MATCH (target:Asset {id: $target_id})
                MERGE (source)-[r:CONNECTED_TO {direction: $direction}]->(target)
                RETURN source.tag_number, target.tag_number
                """,
                source_id=row["source_id"],
                target_id=row["target_id"],
                direction=row["directional_flow"]
            )
            record = await result.single()
            if record:
                relationships_created += 1

    return SeedResponse(
        assets_created=assets_created,
        relationships_created=relationships_created,
        message=f"Seeded {assets_created} assets and {relationships_created} topology relationships"
    )
