# scripts/debug_extraction.py
import sys
sys.path.insert(0, ".")

from src.nodes.ocr_node import extract_fields

raw_text = "MELATONIN S MG"
confidence = 0.91

try:
    result = extract_fields(raw_text, confidence)
    print("drug_name:", result.drug_name)
    print("dosage:", result.dosage)
    print("dosage_unit:", result.dosage_unit)
except Exception as e:
    print("FAILED:", type(e).__name__, str(e))