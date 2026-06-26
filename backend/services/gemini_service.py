import json
from google import genai
from google.genai import types
from config import get_settings

_client = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        settings = get_settings()
        _client = genai.Client(api_key=settings.google_api_key)
    return _client


async def chat_complete(prompt: str) -> str:
    client = _get_client()
    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text


async def extract_knowledge_observation(transcript: str) -> dict:
    client = _get_client()
    prompt = _build_ner_prompt(transcript)
    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return _parse_ner_response(response.text)


def _build_ner_prompt(transcript: str) -> str:
    return f"""You are an industrial equipment knowledge extractor for a manufacturing plant.
Extract structured information from this field operator voice note.

TRANSCRIPT:
{transcript}

Return ONLY a valid JSON object with exactly these fields:
{{
  "target_asset_tag": "<equipment tag like P-101, V-20, B-04, or null if unclear>",
  "observed_issue": "<concise description of the problem or observation>",
  "mitigation_action": "<what was done or recommended, or null>",
  "confidence_index": <float 0.0-1.0 indicating extraction confidence>
}}

Rules:
- target_asset_tag must match known industrial tag patterns (letter prefix + numbers, e.g. P-101)
- If no clear asset tag is mentioned, set target_asset_tag to null
- confidence_index should reflect how clearly the information was stated
- Do not add any explanation outside the JSON object

JSON:"""


def _parse_ner_response(raw: str) -> dict:
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        parts = cleaned.split("```")
        cleaned = parts[1] if len(parts) > 1 else cleaned
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    try:
        return json.loads(cleaned.strip())
    except json.JSONDecodeError:
        return {
            "target_asset_tag": None,
            "observed_issue": raw[:500],
            "mitigation_action": None,
            "confidence_index": 0.1
        }
