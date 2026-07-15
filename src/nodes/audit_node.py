# pyrefly: ignore [missing-import]
from langchain_groq import ChatGroq
from src.state import MedCheckerState
from src.schemas.verdict import ClinicalAuditOutput

def safety_audit_node(state: MedCheckerState) -> dict:
    # Use a medical-preference prompt strategy or a specifically tuned model configuration
    llm = ChatGroq(model="qwen/qwen3-32b", temperature=0.1)
    structured_auditor = llm.with_structured_output(ClinicalAuditOutput)
    
    reasoning_data = state["reasoning_verdict"]
    
    system_prompt = (
        "You are a Senior Medical Safety Auditor. Review the safety decision made by a clinical agent. "
        "Assess how critical/dangerous this interaction is on a scale from 1 (No risk) to 10 (Severe/Fatal injury threat).\n"
        "Also assess the structural accuracy/consistency score (0.0 to 1.0) based on whether the explanation completely "
        "aligns with the given text context without expanding out of bounds."
    )
    
    user_content = f"""
    Context Data: {state['matched_risk_context']}
    Proposed Verdict: {reasoning_data.decision}
    Proposed Explanation: {reasoning_data.explanation}
    """
    
    audit_result = structured_auditor.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ])
    
    # Core Logic Rule: Direct Output vs. Human-in-the-Loop Override
    # High accuracy (> 0.85) and Low emergency level (< 5) can pass straight to the user.
    requires_human = True
    if audit_result.accuracy_score >= 0.85 and audit_result.emergency_level < 5:
        requires_human = False
        
    return {
        "audit_verdict": audit_result,
        "requires_human_intervention": requires_human
    }