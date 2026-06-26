"""
Seeds Bob's field observations as KnowledgeObservation nodes in Neo4j.
Run from backend/ with venv active:
  python ../scripts/seed_tribal_knowledge.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "\\backend")

import asyncio
import uuid
from datetime import datetime, timezone
from neo4j import AsyncGraphDatabase

NEO4J_URI = "bolt://localhost:7687"
NEO4J_AUTH = ("neo4j", "paperbrain123")

OBSERVATIONS = [
    {
        "id": "OBS-BOB-001",
        "author": "Bob Patil",
        "timestamp": "2026-03-14T09:15:00+00:00",
        "transcript": (
            "Every time P-101 vibrates badly during high thermal loads, "
            "V-20 is not fully open. Fix: open V-20 two full rotations counterclockwise. "
            "Vibration drops within 5 minutes. Seen this over 40 times in 15 years."
        ),
        "observed_issue": "Excessive vibration during high thermal load due to V-20 partially closed",
        "mitigation_action": "Open V-20 two full rotations counterclockwise to restore flow",
        "confidence_score": 0.95,
        "target_asset_tag": "P-101",
    },
    {
        "id": "OBS-BOB-002",
        "author": "Bob Patil",
        "timestamp": "2026-03-14T09:22:00+00:00",
        "transcript": (
            "B-04 has no backup feed pump. If P-101 trips, boiler team has 8 minutes, "
            "less in summer heat. No automatic interlock exists. Call on radio immediately. "
            "Pending work order WO-2019-0847 for interlock was never completed."
        ),
        "observed_issue": "No automatic interlock between P-101 trip and B-04 shutdown. Manual radio call required.",
        "mitigation_action": "Radio B-04 control room within 5 minutes of P-101 alarm",
        "confidence_score": 0.92,
        "target_asset_tag": "B-04",
    },
    {
        "id": "OBS-BOB-003",
        "author": "Bob Patil",
        "timestamp": "2026-03-14T09:28:00+00:00",
        "transcript": (
            "V-20 handwheel has been stiff since 2024 packing replacement. "
            "Use extended handle T-EXT-044 from C-block tool cabinet shelf 2. "
            "Without it takes two people to operate in emergency."
        ),
        "observed_issue": "V-20 handwheel stiff due to improperly torqued gland follower after 2024 packing",
        "mitigation_action": "Use extended handle T-EXT-044 from C-block tool cabinet, shelf 2",
        "confidence_score": 0.88,
        "target_asset_tag": "V-20",
    },
]


async def seed():
    driver = AsyncGraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
    created = 0

    async with driver.session() as session:
        for obs in OBSERVATIONS:
            result = await session.run(
                """
                MERGE (o:KnowledgeObservation {id: $id})
                ON CREATE SET
                    o.author = $author,
                    o.timestamp = $timestamp,
                    o.transcript = $transcript,
                    o.observed_issue = $observed_issue,
                    o.mitigation_action = $mitigation_action,
                    o.confidence_score = $confidence_score
                WITH o
                MATCH (a:Asset {tag_number: $tag})
                MERGE (a)-[:HAS_OBSERVATION]->(o)
                RETURN o.id, a.tag_number
                """,
                id=obs["id"],
                author=obs["author"],
                timestamp=obs["timestamp"],
                transcript=obs["transcript"],
                observed_issue=obs["observed_issue"],
                mitigation_action=obs["mitigation_action"],
                confidence_score=obs["confidence_score"],
                tag=obs["target_asset_tag"],
            )
            record = await result.single()
            if record:
                print(f"  Created: {record['o.id']} -> linked to Asset {record['a.tag_number']}")
                created += 1

    await driver.close()
    print(f"\nSeeded {created} KnowledgeObservation nodes.")


if __name__ == "__main__":
    asyncio.run(seed())
