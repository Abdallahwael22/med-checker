from langchain_core.tools import tool
from src.adapters.rxnorm_client import RxNormClient

@tool
def extract_drug_ingredients(drug_name: str) -> dict:
    """
    Resolve a drug name to its active ingredients (IN) using NLM RxNorm.
    
    Args:
        drug_name: The name of the drug (brand name, clinical name, or package description).
        
    Returns:
        A dictionary containing:
        - query_name: The queried drug name.
        - rxcuis: List of matched product RxCUI identifiers.
        - ingredients: List of normalized active ingredient names in lowercase.
    """
    client = RxNormClient()
    info = client.extract_ingredients(drug_name)
    return info.model_dump()
