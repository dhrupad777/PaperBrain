from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pipelines.ingestion_pipeline import ingest_document
from pipelines.voice_pipeline import ingest_voice_note
from models.schemas import IngestDocumentResponse, IngestVoiceResponse

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/document", response_model=IngestDocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    asset_tag: str | None = Form(default=None)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    pdf_bytes = await file.read()
    if len(pdf_bytes) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large. Max 20MB.")

    result = await ingest_document(pdf_bytes, file.filename, asset_tag)

    return IngestDocumentResponse(
        filename=result["filename"],
        chunks_stored=result["chunks_stored"],
        assets_linked=result["assets_linked"],
        message=f"Successfully ingested {result['chunks_stored']} chunks from {file.filename}"
    )


@router.post("/voice", response_model=IngestVoiceResponse)
async def upload_voice(
    file: UploadFile = File(...),
    author: str = Form(default="field_operator")
):
    audio_bytes = await file.read()
    if len(audio_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Audio file too large. Max 10MB.")

    result = await ingest_voice_note(audio_bytes, author)

    if "error" in result:
        raise HTTPException(status_code=422, detail=result["error"])

    return IngestVoiceResponse(
        observation_id=result["observation_id"],
        transcript=result["transcript"],
        asset_linked=result["asset_linked"],
        extracted=result["extracted"],
        message="Voice note processed and stored as KnowledgeObservation"
    )
