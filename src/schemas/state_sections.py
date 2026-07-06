from pydantic import BaseModel
from typing import Optional
from src.schemas.drug_data import OpenFDAResult
from src.schemas.patient import PatientProfile
from src.schemas.verdict import ReasoningVerdict, ConfidenceLevel


class OCRSection(BaseModel):
    """Phase 1 writes this. Phase 2 reads scanned_drug_name."""
    scanned_drug_name: str = ""
    scanned_dosage: str = ""
    ocr_confidence: float = 0.0
    ocr_needs_review: bool = False
    ocr_retry_count: int = 0


class AgentSection(BaseModel):
    """Phase 2 writes this. Phase 3 reads openfda_data."""
    normalized_drug_name: str = ""
    openfda_data: Optional[OpenFDAResult] = None
    agent_trace: str = ""


class ReasoningSection(BaseModel):
    """Phase 3 writes this entirely."""
    patient_profile: Optional[PatientProfile] = None
    llm_verdict: Optional[ReasoningVerdict] = None
    confidence_level: Optional[ConfidenceLevel] = None
    human_review_flag: bool = False
    final_output: str = ""