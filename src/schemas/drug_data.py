from pydantic import BaseModel, Field
from typing import List

class DrugIngredientInfo(BaseModel):
    """
    Model representing resolved active ingredients for a given drug name.
    """
    query_name: str = Field(..., description="The original drug name queried")
    rxcuis: List[str] = Field(default_factory=list, description="Resolved product RxCUIs found")
    ingredients: List[str] = Field(default_factory=list, description="Normalized active ingredient names (e.g. ['atorvastatin'])")
