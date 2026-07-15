from typing import TypedDict, Optional
from src.schemas.state_sections import OCRSection
from src.schemas.drug_data import DrugSafetyProfile
from src.schemas.verdict import ReasoningOutput, ClinicalAuditOutput


class MedCheckerState(TypedDict):
    """
    State for the MedChecker LangGraph workflow.
    Passes data from OCR -> FDA Tooling -> Profile Matching -> Reasoning -> Audit
    """
    
    # --- Phase 1: OCR Intake ---
    raw_image: bytes                                # Raw image bytes for OCR
    patient_id: str                                 # Needed to look up the local JSON profile
    ocr: Optional[OCRSection]                       # OCR structured output
    extracted_drug_name: Optional[str]               # Bridged from OCR for drug_info_node
    ocr_error: Optional[str]                        # Error message if OCR failed
    
    # --- Phase 2: FDA Data Retrieval ---
    safety_profile: Optional[DrugSafetyProfile]     # The nested dict of ingredients and warnings
    
    # --- Phase 3: Aggregation ---
    matched_risk_context: str                       # The compiled string of FDA data + Patient JSON data
    
    # --- Phase 4: Reasoning & Auditing ---
    reasoning_verdict: Optional[ReasoningOutput]    # The LLM's clinical decision and explanation
    audit_verdict: Optional[ClinicalAuditOutput]    # The secondary LLM's safety/accuracy scores
    
    # --- Phase 5: Routing ---
    requires_human_intervention: bool               # Flag to trigger LangGraph's interrupt node
