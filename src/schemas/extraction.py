from pydantic import BaseModel, Field, field_validator


class ExtractedLabel(BaseModel):
    """
    Output of OCR + field extraction.
    Phase 1 (OCR) owns this schema.
    """
    drug_name: str = Field(
        description="Active ingredient, not brand name. e.g. 'melatonin'"
    )
    dosage: str = Field(description="Numeric part only. e.g. '5'")
    dosage_unit: str = Field(description="Unit. e.g. 'mg', 'mcg', 'IU'")
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator("drug_name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("drug_name cannot be empty")
        return v.strip().lower()

    @field_validator("dosage_unit")
    @classmethod
    def clean_unit(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("dosage")
    @classmethod
    def clean_dosage(cls, v: str) -> str:
        return v.strip()