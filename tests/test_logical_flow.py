import os
import json
from dotenv import load_dotenv

# Load environment variables (for GROQ_API_KEY)
load_dotenv()

# Import your state, schemas, and nodes
# pyrefly: ignore [missing-import]
from src.state import MedCheckerState
from src.schemas.drug_data import DrugSafetyProfile, OpenFDALabelInfo
from src.nodes.profile_node import profile_sync_and_match_node
from src.nodes.reasoning_node import clinical_reasoning_node
from src.nodes.audit_node import safety_audit_node

def run_isolated_test():
    print("🚀 Starting Isolated Safety Pipeline Test...\n")

    # ==========================================
    # STEP 1: Mock your colleague's output data
    # ==========================================
    # Let's simulate scanning "Advil" (Ibuprofen) for PATIENT-003 (who takes Warfarin)
    # This should trigger a major bleeding risk warning!
    mock_safety_profile = DrugSafetyProfile(
        query_name="Advil",
        rxcuis=["5640"],
        ingredients=["ibuprofen"],
        safety_profiles={
            "ibuprofen": OpenFDALabelInfo(
                contraindications="Do not use if you have ever had an allergic reaction to any other pain reliever.",
                boxed_warning="WARNING: RISK OF SERIOUS CARDIOVASCULAR AND GASTROINTESTINAL EVENTS. NSAIDs cause an increased risk of serious gastrointestinal inflammatory events including bleeding, ulceration, and perforation of the stomach or intestines, which can be fatal.",
                warnings_and_cautions="Ask a doctor before use if you have stomach problems, high blood pressure, heart disease, liver cirrhosis, or kidney disease.",
                pregnancy="If pregnant or breast-feeding, ask a health professional before use.",
                supplemental_patient_material="Take with food or milk if stomach upset occurs.",
                drug_interactions="Talk to a doctor if you are taking a blood thinner (like warfarin) or steroid medicines.",
                food_interactions="Avoid alcohol while taking this medication."
            )
        }
    )

    # Initialize the LangGraph state exactly how your colleague would hand it off
    state: MedCheckerState = {
        "patient_id": "PATIENT-003",  # Alice Johnson (72yo, Atrial Fibrillation, takes Warfarin)
        "raw_input": "[Mocked OCR Text from Advil Bottle Label]",
        "extracted_drug_name": "Advil",
        "safety_profile": mock_safety_profile,
        "matched_risk_context": "",
        "reasoning_verdict": None,
        "audit_verdict": None,
        "requires_human_intervention": False
    }

    # ==========================================
    # STEP 2: Execute Your Core Pipeline Logic
    # ==========================================
    
    # 1. Run your Profile Matching Node
    print("📋 [1/3] Running Profile Matcher Node...")
    profile_updates = profile_sync_and_match_node(state)
    state.update(profile_updates) # Update the state dict dynamically
    print("✅ Profile contextualized successfully.")
    print("-" * 50)
    print("Generated Context sent to LLM:")
    print(state["matched_risk_context"])
    print("-" * 50)

    # 2. Run your Clinical Reasoning Node
    print("\n🧠 [2/3] Invoking Clinical Reasoning Engine (Groq Llama-3)...")
    reasoning_updates = clinical_reasoning_node(state)
    state.update(reasoning_updates)
    
    verdict = state["reasoning_verdict"]
    print(f"✅ Reasoning Complete.")
    print(f"👉 DECISION: {verdict.decision}")
    print(f"👉 EXPLANATION: {verdict.explanation}")
    print(f"👉 DETECTED MATCHES: {verdict.detected_matches}")
    print("-" * 50)

    # 3. Run your Safety Audit Node
    print("\n🛡️ [3/3] Running Safety Audit and Gatekeeper Node...")
    audit_updates = safety_audit_node(state)
    state.update(audit_updates)
    
    audit = state["audit_verdict"]
    print(f"✅ Audit Complete.")
    print(f"👉 ACCURACY SCORE: {audit.accuracy_score}")
    print(f"👉 EMERGENCY LEVEL (1-10): {audit.emergency_level}")
    print(f"👉 ROUTING ROUTE: {'🚨 HUMAN INTERVENTION REQUIRED' if state['requires_human_intervention'] else '🟢 DIRECT PASS TO USER'}")
    print("=" * 50)
    print("\n🎉 Isolated pipeline test finished successfully!")

if __name__ == "__main__":
    run_isolated_test()