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
    Uses minimum — weakest region determines overall reliability.
    Returns 0.0 if no text was detected.
    """
    # The problem this function solves:
    # - The OCR engine returns a list of text regions with their confidence scores.
    # - We need to aggregate the confidence scores to get a single confidence score for the entire image.
    # - We use the minimum confidence score as the overall confidence score.
    # - This is because the weakest region determines the overall reliability of the OCR results.
    if not raw_result:
        return 0.0
    scores = [line[1][1] for line in raw_result if line and line[1]]
    if not scores:
        return 0.0
    return min(scores)


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


def _attempt_ocr(img: np.ndarray, aggressive: bool) -> tuple[list, float]:
    """Run one OCR attempt. Returns (raw_result, confidence)."""
    # The problem this function solves:
    # - We need to run OCR on the image.
    # - We use the aggressive or basic preprocessing functions to preprocess the image.
    # - We use the deskew function to deskew the image.
    # - We use the run_paddleocr function to run OCR on the image.
    # - We return the raw results and the confidence score.
    processed = aggressive_preprocess(img) if aggressive else basic_preprocess(img)
    processed = deskew(processed)
    raw = run_paddleocr(processed)
    return raw, compute_confidence(raw)


def ocr_node(state: MedCheckerState) -> MedCheckerState:
    confidence = 0.0

    try:
        img = decode_image(state["raw_image"])
    except Exception:
        state["ocr"] = OCRSection(
            scanned_drug_name="",
            scanned_dosage="",
            ocr_confidence=0.0,
            ocr_needs_review=True,
            ocr_retry_count=0
        )
        state["extracted_drug_name"] = None
        return state

    for attempt in range(settings.ocr_max_retries + 1):
        try:
            raw_result, confidence = _attempt_ocr(img, aggressive=(attempt > 0))

            if confidence >= settings.ocr_confidence_threshold:
                raw_text = " ".join([
                    line[1][0] for line in raw_result if line and line[1]
                ])
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
        except Exception:
            continue

    # All retries exhausted
    # Only reached if all OCR attempts (including retries) fail to meet the confidence threshold.
    # Sets the OCR section to indicate failure and that manual review is required.
    state["ocr"] = OCRSection(
        scanned_drug_name="",
        scanned_dosage="",
        ocr_confidence=confidence,
        ocr_needs_review=True,
        ocr_retry_count=settings.ocr_max_retries
    )
    state["extracted_drug_name"] = None
    return state
