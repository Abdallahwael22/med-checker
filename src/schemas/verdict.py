from pydantic import BaseModel, Field
from enum import Enum


class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ReasoningOutput(BaseModel):
    decision: str = Field(description="Must be exactly 'APPROVE', 'DENY', or 'HOLD_FOR_REVIEW'")
    explanation: str = Field(description="A plain-language clinical explanation of why this drug is safe or dangerous for this specific profile")
    detected_matches: list[str] = Field(description="The specific overlapping contradictions found between the FDA profile and patient history")

class ClinicalAuditOutput(BaseModel):
    accuracy_score: float = Field(description="Confidence/Accuracy assessment score from 0.0 to 1.0 based on clinical reference grounding")
    emergency_level: int = Field(description="Risk/Emergency level score from 1 (No risk) to 10 (Fatal interaction hazard)")
