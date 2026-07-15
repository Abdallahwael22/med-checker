from pydantic import BaseModel, Field

class DrugNameExtraction(BaseModel):
    """
    Model used for structured extraction of drug names from user text.
    """
    standardized_name: str = Field(
        ..., 
        description="The clean, standard generic or brand name of the drug extracted from the input text."
    )
