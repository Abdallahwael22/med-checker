from langgraph.graph import StateGraph, START, END

from src.state import MedCheckerState
from src.nodes.ocr_node import ocr_node
from src.nodes.drug_info_node import fetch_drug_safety_node
from src.nodes.profile_node import profile_sync_and_match_node
from src.nodes.reasoning_node import clinical_reasoning_node
from src.nodes.audit_node import safety_audit_node


def build_graph() -> StateGraph:
    """
    Build and compile the MedChecker LangGraph workflow.

    Flow:
        OCR → Drug Info (FDA) → Profile Matching → Clinical Reasoning → Safety Audit → END
    """
    builder = StateGraph(MedCheckerState)

    # --- Register nodes ---
    builder.add_node("ocr", ocr_node)
    builder.add_node("drug_info", fetch_drug_safety_node)
    builder.add_node("profile_match", profile_sync_and_match_node)
    builder.add_node("reasoning", clinical_reasoning_node)
    builder.add_node("audit", safety_audit_node)

    # --- Define edges ---
    builder.add_edge(START, "ocr")
    builder.add_edge("ocr", "drug_info")
    builder.add_edge("drug_info", "profile_match")
    builder.add_edge("profile_match", "reasoning")
    builder.add_edge("reasoning", "audit")
    builder.add_edge("audit", END)

    return builder.compile()


# Compiled graph instance — import this to run the workflow
graph = build_graph()
