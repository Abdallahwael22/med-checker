from typing import TypedDict, Optional, Any

class MedCheckerState(TypedDict):
    """
    State for the MedChecker LangGraph workflow.
    """
    raw_input: str                    # this is ocr ouptput  TODO: needs to be adjusted
    extracted_drug_name: Optional[str]  # this is of the first agent ouput  
    safety_profile: Optional[dict]     
    # Future nodes (e.g. Profile, Reasoning, Audit) can append fields here
