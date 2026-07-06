from typing import TypedDict, Optional
from src.schemas.state_sections import OCRSection, AgentSection, ReasoningSection


class MedCheckerState(TypedDict):
    raw_image: bytes
    patient_id: str
    ocr: Optional[OCRSection]
    agent: Optional[AgentSection]
    reasoning: Optional[ReasoningSection]
    audit_log: dict