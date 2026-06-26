import uuid
from datetime import datetime, timezone
from services.speech_service import transcribe_audio
from services.gemini_service import extract_knowledge_observation
from database.neo4j_client import get_driver


async def ingest_voice_note(audio_bytes: bytes, author: str = "field_operator") -> dict:
    transcript = await transcribe_audio(audio_bytes)
    if not transcript:
        return {"error": "No speech detected in audio", "transcript": ""}

    extracted = await extract_knowledge_observation(transcript)

    obs_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    driver = await get_driver()
    asset_linked = None

    async with driver.session() as session:
        await session.run(
            """
            CREATE (o:KnowledgeObservation {
                id: $id,
                author: $author,
                timestamp: $timestamp,
                transcript: $transcript,
                observed_issue: $observed_issue,
                mitigation_action: $mitigation_action,
                confidence_score: $confidence_score
            })
            """,
            id=obs_id,
            author=author,
            timestamp=timestamp,
            transcript=transcript,
            observed_issue=extracted.get("observed_issue", ""),
            mitigation_action=extracted.get("mitigation_action") or "",
            confidence_score=float(extracted.get("confidence_index", 0.5))
        )

        target_tag = extracted.get("target_asset_tag")
        if target_tag:
            result = await session.run(
                """
                MATCH (a:Asset {tag_number: $tag})
                MATCH (o:KnowledgeObservation {id: $obs_id})
                MERGE (a)-[:HAS_OBSERVATION]->(o)
                RETURN a.tag_number
                """,
                tag=target_tag,
                obs_id=obs_id
            )
            record = await result.single()
            if record:
                asset_linked = record["a.tag_number"]

    return {
        "transcript": transcript,
        "observation_id": obs_id,
        "asset_linked": asset_linked,
        "extracted": extracted
    }
