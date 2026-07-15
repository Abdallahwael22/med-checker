import json
from src.state import MedCheckerState

def profile_sync_and_match_node(state: MedCheckerState) -> dict:
    patient_id = state["patient_id"]
    fda_profile = state["safety_profile"]
        
    # 1. Load the localized user profile database
    with open("data/patients/patient_profiles.json", "r") as f:
        profiles_db = json.load(f)
    
    patient_data = profiles_db.get(patient_id, {})
    
    # 2. Extract Patient Metadata
    age = patient_data.get("metadata", {}).get("age", "Unknown")
    chronic_diseases = patient_data.get("diseases", [])
    allergies = patient_data.get("allergies", [])
    current_meds = patient_data.get("current_medications", [])
    
    # 3. Aggregate FDA Data from the Schema
    fda_context_blocks = []
    if fda_profile and fda_profile.safety_profiles:
        for ingredient, safety_info in fda_profile.safety_profiles.items():
            if safety_info:
                block = f"""
                -- Ingredient: {ingredient.upper()} --
                Contraindications: {safety_info.contraindications or 'None reported'}
                Boxed Warnings: {safety_info.boxed_warning or 'None reported'}
                Drug Interactions: {safety_info.drug_interactions or 'None reported'}
                Food Interactions: {safety_info.food_interactions or 'None reported'}
                Warnings/Cautions: {safety_info.warnings_and_cautions or 'None reported'}
                """
                fda_context_blocks.append(block)
                
    fda_compiled_text = "\n".join(fda_context_blocks)

    # 4. Build the final prompt context for the LLM
    matched_context = f"""
    --- PATIENT MEDICAL PROFILE ---
    Age: {age}
    Known Conditions/Diseases: {', '.join(chronic_diseases) if chronic_diseases else 'None'}
    Allergies: {', '.join(allergies) if allergies else 'None'}
    Current Active Medications: {', '.join(current_meds) if current_meds else 'None'}
    
    --- NEW SCANNED DRUG WARNINGS (FDA) ---
    Target Medicine Scanned: {fda_profile.query_name if fda_profile else 'Unknown'}
    {fda_compiled_text}
    """
    
    return {"matched_risk_context": matched_context}