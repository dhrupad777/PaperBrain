# OCR wrapper
import re
import os
from pathlib import Path
from typing import List
import pytesseract
from PIL import Image

# Try to set Tesseract path for Windows (common installation location)
if os.name == 'nt':  # Windows
    tesseract_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    ]
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break

def run_ocr(image_path: str) -> List[str]:
    """
    Run OCR on an image file and return tokenized text.
    
    Args:
        image_path: Path to image file (PNG, JPG, etc.)
    
    Returns:
        List of tokens extracted from the image
    """
    img = Image.open(image_path).convert("RGB")
    text = pytesseract.image_to_string(img)
    
    # Tokenize: extract words/numbers
    tokens = re.findall(r"[A-Za-z0-9₹.,/%\-]+", text)
    return tokens
