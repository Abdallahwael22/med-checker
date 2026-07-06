from pydantic import BaseModel
from typing import Optional


class OpenFDAResult(BaseModel):
    """STUB — Phase 2 will fill this out."""
    drug_name: str = ""
    normalized_name: str = ""
    found_in_openfda: bool = False