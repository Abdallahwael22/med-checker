from pydantic import BaseModel
from enum import Enum


class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ReasoningVerdict(BaseModel):
    """STUB — Phase 3 will fill this out."""
    human_review_required: bool = False