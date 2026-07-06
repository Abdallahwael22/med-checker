from pydantic import BaseModel


class PatientProfile(BaseModel):
    """STUB — Phase 3 will fill this out."""
    patient_id: str = ""
    name: str = ""