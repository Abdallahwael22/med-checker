from typing import TypedDict, Optional, Dict, Any
from src.schemas.drug_data import DrugSafetyProfile
from src.schemas.verdict import ReasoningOutput, ClinicalAuditOutput

class MedCheckerState(TypedDict):
    """
    State for the MedChecker LangGraph workflow.
    Passes data from OCR/Extraction -> FDA Tooling -> Profile Matching -> Reasoning -> Audit
    """
    
    # --- Phase 1: Intake & Extraction (Your Colleague's Output) ---
    patient_id: str                   # Needed to look up the local JSON profile
    raw_input: str                    # The raw OCR text or image file path
    extracted_drug_name: Optional[str] 
    
    # --- Phase 2: FDA Data Retrieval ---
    safety_profile: Optional[DrugSafetyProfile]  # The nested dict of ingredients and warnings
    
    # --- Phase 3: Aggregation (Your Tasks Begin Here) ---
    matched_risk_context: str         # The compiled string of FDA data + Patient JSON data
    
    # --- Phase 4: Reasoning & Auditing ---
    reasoning_verdict: Optional[ReasoningOutput] # The LLM's clinical decision and explanation
    audit_verdict: Optional[ClinicalAuditOutput] # The secondary LLM's safety/accuracy scores
    
    # --- Phase 5: Routing ---
    requires_human_intervention: bool # Flag to trigger LangGraph's interrupt node
