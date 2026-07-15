from src.state import MedCheckerState
from src.schemas.state_sections import OCRSection
from src.schemas.extraction import ExtractedLabel
from src.adapters.ocr_engine import run_paddleocr
from src.nodes.preprocessing import (
    decode_image,
    basic_preprocess,
    aggressive_preprocess,
    deskew
)
from src.config import settings
from langchain_groq import ChatGroq

import numpy as np

_extractor = None

def get_extractor():
    # The problem this function solves:
    # - We need to extract the drug or supplement details from the OCR results.
    # - We use a LLM with Pydantic structured output to extract the details.
    # - We return a valid ExtractedLabel or raise a ValidationError if the extraction fails.
    global _extractor
    if _extractor is None:
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY is not set in .env")
        llm = ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_api_key
        )
        _extractor = llm.with_structured_output(ExtractedLabel)
    return _extractor


def compute_confidence(raw_result: list) -> float:
    """
    Aggregate OCR confidence across all detected text regions.
    Uses average (mean) of all regions to represent overall reliability.
    Returns 0.0 if no text was detected.
    """
    if not raw_result:
        return 0.0
    scores = [line[1][1] for line in raw_result if line and line[1]]
    if not scores:
        return 0.0
    return sum(scores) / len(scores)


def extract_fields(raw_text: str, confidence: float) -> ExtractedLabel:
    """
    Convert raw OCR text into a structured ExtractedLabel.
    Uses LLM with Pydantic structured output — always returns
    a valid ExtractedLabel or raises ValidationError.
    """
    prompt = f"""Extract the drug or supplement details from this label text.

Rules:
- Return the ACTIVE INGREDIENT name, not the brand name
  (e.g. return 'melatonin' not 'Nature\\'s Bounty')
- Return only the numeric dosage in the dosage field
  (e.g. '5' not '5mg')
- Return the unit separately
  (e.g. 'mg', 'mcg', 'IU', 'g')
- Set confidence to exactly {round(confidence, 4)}
- If you cannot find the dosage, return an empty string

Label text:
{raw_text}
"""
    return get_extractor().invoke(prompt)





def ocr_node(state: MedCheckerState) -> MedCheckerState:
    confidence = 0.0
    attempt_errors: list[str] = []

    try:
        img = decode_image(state["raw_image"])
    except Exception as e:
        state["ocr"] = OCRSection(
            scanned_drug_name="",
            scanned_dosage="",
            ocr_confidence=0.0,
            ocr_needs_review=True,
            ocr_retry_count=0
        )
        state["extracted_drug_name"] = None
        # Store decode error so the UI can surface it
        state["ocr_error"] = f"Image decode failed: {e}"
        return state

    for attempt in range(settings.ocr_max_retries + 1):
        try:
            if attempt == 0:
                prep_desc = "raw color image"
                processed = img
            elif attempt == 1:
                prep_desc = "basic preprocessing (grayscale + equalize + sharpen + deskew)"
                processed = basic_preprocess(img)
                processed = deskew(processed)
            else:
                prep_desc = "aggressive preprocessing (denoise + Otsu threshold + deskew)"
                processed = aggressive_preprocess(img)
                processed = deskew(processed)

            raw_result = run_paddleocr(processed)
            confidence = compute_confidence(raw_result)

            # Reconstruct raw text
            raw_text = " ".join([
                line[1][0] for line in raw_result if line and line[1]
            ])

            # Debug printing to see exactly what PaddleOCR found
            print("\n" + "-"*50)
            print(f"[OCR DEBUG] Attempt {attempt} ({prep_desc})")
            print(f"  Combined Raw Text: '{raw_text}'")
            print(f"  Calculated Average Confidence: {confidence:.4f}")
            if raw_result:
                min_c = min([line[1][1] for line in raw_result if line and line[1]])
                print(f"  Minimum Box Confidence:        {min_c:.4f}")
                print("  Individual detected text lines:")
                for line in raw_result:
                    if line and line[1]:
                        print(f"    - '{line[1][0]}' (conf: {line[1][1]:.4f})")
            print("-"*50 + "\n")

            if confidence < settings.ocr_confidence_threshold:
                attempt_errors.append(
                    f"Attempt {attempt}: confidence {confidence:.3f} below threshold "
                    f"{settings.ocr_confidence_threshold} ({prep_desc})"
                )
                continue

            extracted = extract_fields(raw_text, confidence)
            state["ocr"] = OCRSection(
                scanned_drug_name=extracted.drug_name,
                scanned_dosage=f"{extracted.dosage}{extracted.dosage_unit}",
                ocr_confidence=confidence,
                ocr_needs_review=False,
                ocr_retry_count=attempt
            )
            state["extracted_drug_name"] = extracted.drug_name
            return state

        except Exception as e:
            print(f"[OCR ERROR] Attempt {attempt} failed with exception: {type(e).__name__}: {e}")
            attempt_errors.append(f"Attempt {attempt} error: {type(e).__name__}: {e}")
            continue

    # All retries exhausted — return gracefully with error info in state
    error_summary = "\n".join(attempt_errors) if attempt_errors else "No attempts succeeded."
    state["ocr"] = OCRSection(
        scanned_drug_name="",
        scanned_dosage="",
        ocr_confidence=confidence,
        ocr_needs_review=True,
        ocr_retry_count=settings.ocr_max_retries
    )
    state["extracted_drug_name"] = None
    state["ocr_error"] = (
        f"OCR failed after {settings.ocr_max_retries + 1} attempts "
        f"(threshold={settings.ocr_confidence_threshold}):\n{error_summary}"
    )
    return state
