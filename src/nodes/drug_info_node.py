from src.state import MedCheckerState
from src.tools.drug_safety_tool import get_drug_safety_info

def fetch_drug_safety_node(state: MedCheckerState) -> dict:
    """
    Node that fetches safety information for the extracted drug name.
    """
    drug_name = state.get("extracted_drug_name")
    
    if not drug_name:
        return {"safety_profile": None}
        
    # Call the tool directly
    try:
        # get_drug_safety_info returns a dict representation of DrugSafetyProfile
        result = get_drug_safety_info.invoke({"drug_name": drug_name})
        return {"safety_profile": result}
    except Exception as e:
        print(f"Error fetching safety info for {drug_name}: {e}")
        return {"safety_profile": None}
