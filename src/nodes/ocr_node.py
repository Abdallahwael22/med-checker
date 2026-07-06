from src.state import MedCheckerState
from src.schemas.state_sections import OCRSection


def ocr_node(state: MedCheckerState) -> MedCheckerState:
    """STUB — Phase 1 will implement this."""
    print("[ocr_node] stub running")
    state["ocr"] = OCRSection()
    return state

def compute_confidence(raw_result: list) -> float:
    """
    Aggregate OCR confidence across all detected text regions.
    Uses minimum — weakest region determines overall reliability.
    Returns 0.0 if no text was detected.
    """
    if not raw_result:
        return 0.0
    scores = [line[1][1] for line in raw_result if line and line[1]]
    if not scores:
        return 0.0
    return min(scores)