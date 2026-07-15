# pyrefly: ignore [missing-import]
from langchain_core.tools import tool
# pyrefly: ignore [missing-import]
from src.adapters.rxnorm_client import RxNormClient
# pyrefly: ignore [missing-import]
from src.adapters.openfda_client import OpenFDAClient
# pyrefly: ignore [missing-import]
from src.schemas.drug_data import DrugSafetyProfile

@tool
def get_drug_safety_info(drug_name: str) -> dict:
    """
    Retrieve structured safety information, contraindications, warnings, and drug/food interactions
    for a drug by its brand or generic name.
    
    This tool retrieves the raw safety parameters from regulatory label databases; it does not 
    perform medical decision-making or check compatibility against a specific patient profile.
    
    Args:
        drug_name: The brand name, generic name, or description of the drug to look up.
        
    Returns:
        A dict containing active ingredients, RxCUIs, and safety profiles for each ingredient.
    """
    rxnorm_client = RxNormClient()
    openfda_client = OpenFDAClient()
    
    # 1. Resolve active ingredients (returns a dict)
    ingredients_info = rxnorm_client.extract_ingredients(drug_name)
    ingredients = ingredients_info.get("ingredients") or []
    rxcuis = ingredients_info.get("rxcuis") or []
    
    # 2. Fetch safety labels for each ingredient
    safety_profiles = {}
    for ingredient in ingredients:
        label = openfda_client.get_label_by_ingredient(ingredient)
        safety_profiles[ingredient] = label
        
    profile = DrugSafetyProfile(
        query_name=drug_name,
        rxcuis=rxcuis,
        ingredients=ingredients,
        safety_profiles=safety_profiles
    )
    return profile.model_dump()
