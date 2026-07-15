from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class OpenFDALabelInfo(BaseModel):
    """
    Model representing safety, warning, and interaction details from an OpenFDA drug label.
    """
    # Absolute Blocks
    contraindications: Optional[str] = Field(None, description="Absolute reasons to block the drug")
    boxed_warning: Optional[str] = Field(None, description="Critical, life-threatening boxed warnings (Black Box Warning)")
    
    # Physical & Demographic Risks
    warnings_and_cautions: Optional[str] = Field(None, description="Warnings and cautions section narrative")
    pregnancy: Optional[str] = Field(None, description="Safety data regarding pregnant patients")
    supplemental_patient_material: Optional[str] = Field(None, description="Plain-language patient instructions or material")
    
    # Environmental & Lifestyle Conflicts
    drug_interactions: Optional[str] = Field(None, description="Chemical and drug interactions narrative")
    food_interactions: Optional[str] = Field(None, description="Dietary restrictions or conflicts narrative")

class DrugSafetyProfile(BaseModel):
    """
    Model representing the complete safety report for a drug name.
    Includes active ingredients and their corresponding safety profiles.
    """
    query_name: str = Field(..., description="The original drug name queried")
    rxcuis: List[str] = Field(default_factory=list, description="Resolved RxCUIs")
    ingredients: List[str] = Field(default_factory=list, description="Active ingredient names")
    safety_profiles: Dict[str, Optional[OpenFDALabelInfo]] = Field(
        default_factory=dict, 
        description="Safety profile for each active ingredient"
    )
