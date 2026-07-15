# scripts/debug_ocr.py
from src.adapters.ocr_engine import run_paddleocr
from src.nodes.preprocessing import decode_image, basic_preprocess, deskew

with open("data/samples/melatonin_clean.jpg", "rb") as f:
    img_bytes = f.read()

img = decode_image(img_bytes)
processed = basic_preprocess(img)
processed = deskew(processed)
result = run_paddleocr(processed)

print("OCR detected text:")
for line in result:
    if line and line[1]:
        print(f"  text: '{line[1][0]}'  confidence: {line[1][1]:.2f}")