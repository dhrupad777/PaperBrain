import cv2
import pytesseract
import numpy as np
import re
import os
from pathlib import Path
from PIL import Image

# Try to set Tesseract path for Windows
if os.name == 'nt':  # Windows
    tesseract_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    ]
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break

def ocr_tokens(png_path):
    print("✅ USING OPENCV OCR v5 (scan mode) on:", png_path)
    
    # Read
    img = cv2.imread(str(png_path))
    
    # If OpenCV can't read, try PIL fallback
    if img is None:
        pil_img = Image.open(png_path).convert("RGB")
        img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    
    # 1) Resize (upscale)
    img = cv2.resize(img, None, fx=1.8, fy=1.8, interpolation=cv2.INTER_CUBIC)
    
    # 2) Convert to LAB color space (better contrast control)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # 3) CLAHE on L-channel (AMAZING for photos)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    
    # Merge back
    limg = cv2.merge((cl, a, b))
    img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    
    # 4) Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 5) Otsu Threshold (less harsh than adaptive)
    _, thr = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # 6) Slight morphology to restore broken text
    kernel = np.ones((2,2), np.uint8)
    thr = cv2.morphologyEx(thr, cv2.MORPH_CLOSE, kernel)
    
    # Save debug
    debug_path = Path("storage/uploads/debug_preprocessed.png")
    debug_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(debug_path), thr)
    print("🖼️ Saved preprocessed (scan mode) ->", debug_path)
    
    # OCR
    text = pytesseract.image_to_string(thr, config="--oem 3 --psm 6")
    tokens = re.findall(r"[A-Za-z0-9₹.,:/\-]+", text)
    
    return text, tokens

def run_ocr(image_path: str):
    """
    Legacy function for backward compatibility.
    Returns only tokens.
    """
    _, tokens = ocr_tokens(image_path)
    return tokens

if __name__ == "__main__":
    text, tokens = ocr_tokens("test.png")
    print("=== RAW OCR TEXT ===")
    print(text[:3000])
    print("\n=== TOKENS (200) ===")
    print(tokens[:200])
    print("Total:", len(tokens))
