from langchain_core.tools import tool
from typing import List, Dict, Optional
from src.adapters.openfda_client import OpenFDAClient

@tool
def fetch_drug_labels_from_openfda(ingredients: List[str]) -> Dict[str, Optional[dict]]:
    """
    Query OpenFDA for safety profiles, warnings, and drug interactions for a list of active ingredients.
    
    Args:
        ingredients: A list of active ingredient names (e.g. ['atorvastatin', 'amoxicillin']).
        
    Returns:
        A dictionary mapping each ingredient to its parsed OpenFDA safety profile schema
        (or None if not found/error).
    """
    client = OpenFDAClient()
    results = {}
    for ingredient in ingredients:
        label_info = client.get_label_by_ingredient(ingredient)
        results[ingredient] = label_info.model_dump() if label_info else None
    return results
