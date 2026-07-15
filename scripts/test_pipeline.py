"""
Quick test: run the full MedChecker graph with a real drug image.
Usage:  uv run python scripts/test_pipeline.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.graph import graph

IMAGE_PATH = r"C:\Users\tarek\Downloads\WhatsApp Image 2026-07-15 at 2.48.35 PM.jpeg"
PATIENT_ID = "PATIENT-003"

def main():
    # 1. Read image as bytes (what the graph expects)
    with open(IMAGE_PATH, "rb") as f:
        raw_image = f.read()
    print(f"[OK] Loaded image ({len(raw_image):,} bytes)")

    # 2. Build initial state
    initial_state = {
        "raw_image": raw_image,
        "patient_id": PATIENT_ID,
    }

    # 3. Run the graph
    print("[..] Running pipeline: OCR -> Drug Info -> Profile -> Reasoning -> Audit\n")
    result = graph.invoke(initial_state)

    # 4. Print results
    print("=" * 60)
    print("PIPELINE RESULTS")
    print("=" * 60)

    ocr = result.get("ocr")
    if ocr:
        print(f"\n[OCR]")
        print(f"   Drug Name:   {ocr.scanned_drug_name}")
        print(f"   Dosage:      {ocr.scanned_dosage}")
        print(f"   Confidence:  {ocr.ocr_confidence:.4f}")
        print(f"   Needs Review: {ocr.ocr_needs_review}")

    print(f"\n[EXTRACTED] Drug Name: {result.get('extracted_drug_name')}")

    safety = result.get("safety_profile")
    if safety:
        print(f"\n[FDA SAFETY]")
        print(f"   Query:       {safety.query_name}")
        print(f"   Ingredients: {safety.ingredients}")
        for ing, info in safety.safety_profiles.items():
            if info:
                print(f"\n   [{ing.upper()}]")
                print(f"   Contraindications: {info.contraindications or 'None'}")
                print(f"   Boxed Warning:     {info.boxed_warning or 'None'}")
                print(f"   Drug Interactions: {info.drug_interactions or 'None'}")

    verdict = result.get("reasoning_verdict")
    if verdict:
        print(f"\n[REASONING]")
        print(f"   Decision:    {verdict.decision}")
        print(f"   Explanation: {verdict.explanation}")
        print(f"   Matches:     {verdict.detected_matches}")

    audit = result.get("audit_verdict")
    if audit:
        print(f"\n[AUDIT]")
        print(f"   Accuracy:    {audit.accuracy_score}")
        print(f"   Emergency:   {audit.emergency_level}")

    print(f"\n[ROUTING] Requires Human Intervention: {result.get('requires_human_intervention')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
