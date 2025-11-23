from google.cloud import vision
import re
import os
from pathlib import Path

def ocr_tokens_gcp(image_path):
    """
    Google Cloud Vision API OCR.
    Passes original image directly - GCP handles preprocessing.
    Returns: (text, tokens)
    """
    # Verify credentials are set
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set. Set it in your terminal: $env:GOOGLE_APPLICATION_CREDENTIALS='C:\\Paper Brain ANN\\gcp-key.json'")
    
    client = vision.ImageAnnotatorClient()
    
    # Read image file directly - no preprocessing
    with open(image_path, "rb") as f:
        content = f.read()
    
    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)
    
    if response.error.message:
        raise RuntimeError(f"GCP Vision API error: {response.error.message}")
    
    text = response.full_text_annotation.text or ""
    tokens = re.findall(r"[A-Za-z0-9₹.,:/\-]+", text)
    
    return text, tokens

