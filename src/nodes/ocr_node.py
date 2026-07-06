from src.state import MedCheckerState
from src.schemas.state_sections import OCRSection


def ocr_node(state: MedCheckerState) -> MedCheckerState:
    """STUB — Phase 1 will implement this."""
    print("[ocr_node] stub running")
    state["ocr"] = OCRSection()
    return state