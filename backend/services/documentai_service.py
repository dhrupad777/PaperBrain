import asyncio
from google.cloud import documentai_v1 as documentai
from config import get_settings


def _get_processor_name() -> str:
    settings = get_settings()
    return (
        f"projects/{settings.google_cloud_project}"
        f"/locations/{settings.documentai_location}"
        f"/processors/{settings.documentai_processor_id}"
    )


async def extract_text_from_pdf(pdf_bytes: bytes, filename: str) -> list[dict]:
    client = documentai.DocumentProcessorServiceClient()
    processor_name = _get_processor_name()

    raw_document = documentai.RawDocument(
        content=pdf_bytes,
        mime_type="application/pdf"
    )
    request = documentai.ProcessRequest(
        name=processor_name,
        raw_document=raw_document
    )

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, client.process_document, request)

    return _split_into_chunks(result.document, filename)


def _split_into_chunks(document, source_file: str) -> list[dict]:
    chunks = []
    for page_num, page in enumerate(document.pages, start=1):
        page_text = _extract_page_text(document.text, page)
        if not page_text.strip():
            continue
        for sub in _chunk_text(page_text, max_chars=1500, overlap_chars=150):
            chunks.append({
                "page_number": page_num,
                "chunk_text": sub,
                "source_file": source_file
            })
    return chunks


def _extract_page_text(full_text: str, page) -> str:
    segments = []
    for token in page.tokens:
        for seg in token.layout.text_anchor.text_segments:
            start = int(seg.start_index) if seg.start_index else 0
            end = int(seg.end_index)
            segments.append(full_text[start:end])
    return " ".join(segments)


def _chunk_text(text: str, max_chars: int = 1500, overlap_chars: int = 150) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunks.append(text[start:end])
        start = end - overlap_chars
    return chunks
