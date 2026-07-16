# scripts/debug_ocr2.py
import sys
sys.path.insert(0, ".")

import cv2
import numpy as np
from src.adapters.ocr_engine import run_paddleocr
from src.nodes.preprocessing import decode_image, basic_preprocess, deskew

IMAGE_PATH = "data/samples/Omega3.jpg"

with open(IMAGE_PATH, "rb") as f:
    img_bytes = f.read()

# Step 1 — decode
img = decode_image(img_bytes)
print(f"Original shape: {img.shape}")

# Step 2 — preprocess
processed = basic_preprocess(img)
print(f"After basic_preprocess shape: {processed.shape}")

# Step 3 — deskew
processed = deskew(processed)
print(f"After deskew shape: {processed.shape}")

# Step 4 — run OCR directly on original (no preprocessing)
print("\n--- OCR on ORIGINAL image (no preprocessing) ---")
result_original = run_paddleocr(img)
print(f"Result: {result_original}")

# Step 5 — run OCR on preprocessed
print("\n--- OCR on PREPROCESSED image ---")
result_processed = run_paddleocr(processed)
print(f"Result: {result_processed}")