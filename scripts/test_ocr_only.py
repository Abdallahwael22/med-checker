# scripts/test_ocr_only.py
import sys
sys.path.insert(0, ".")

from src.nodes.ocr_node import ocr_node

IMAGE_PATH = "data/samples/blurry_label.jpg"

with open(IMAGE_PATH, "rb") as f:
    raw_image = f.read()

state = {
    "raw_image": raw_image,
    "patient_id": "patient_001",
    "ocr": None,
    "agent": None,
    "reasoning": None,
    "audit_log": {}
}

result = ocr_node(state)
ocr = result["ocr"]
print(f"Drug Name:    {ocr.scanned_drug_name}")
print(f"Dosage:       {ocr.scanned_dosage}")
print(f"Confidence:   {ocr.ocr_confidence:.4f}")
print(f"Needs Review: {ocr.ocr_needs_review}")