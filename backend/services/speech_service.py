import asyncio
from google.cloud import speech_v1 as speech


async def transcribe_audio(audio_bytes: bytes) -> str:
    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(content=audio_bytes)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
        sample_rate_hertz=48000,
        language_code="en-IN",
        enable_automatic_punctuation=True,
        model="latest_long"
    )

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: client.recognize(config=config, audio=audio)
    )

    transcript = " ".join(
        result.alternatives[0].transcript
        for result in response.results
        if result.alternatives
    )
    return transcript.strip()
