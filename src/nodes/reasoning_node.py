# pyrefly: ignore [missing-import]
from langchain_groq import ChatGroq
from src.state import MedCheckerState
from src.schemas.verdict import ReasoningOutput

def clinical_reasoning_node(state: MedCheckerState) -> dict:
    # Initialize your model (using Groq for rapid structural extraction)
    llm = ChatGroq(model="qwen/qwen3-32b", temperature=0.0)
    structured_llm = llm.with_structured_output(ReasoningOutput)
    
    system_prompt = (
        "You are an expert clinical pharmacologist. Your task is to evaluate if a patient "
        "can safely take a new medication based on their current patient file and the drug's FDA warnings.\n"
        "Analyze whether the patient's existing diseases cross with the drug's contraindications, "
        "or if their current medications cross with the drug's interactions."
    )
    
    user_content = f"Evaluate safety parameters for the following clinical case:\n{state['matched_risk_context']}"
    
    # Request structured completion
    verdict = structured_llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ])
    
    return {"reasoning_verdict": verdict}