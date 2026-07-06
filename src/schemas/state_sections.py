from pydantic import BaseModel


class OCRSection(BaseModel):
    """
    Phase 1 writes this. Phase 2 reads scanned_drug_name.
    """
    scanned_drug_name: str = ""
    scanned_dosage: str = ""
    ocr_confidence: float = 0.0
    ocr_needs_review: bool = False
    ocr_retry_count: int = 0