import pytest
from unittest.mock import patch, MagicMock
from src.state import MedCheckerState
from src.nodes.agent_node import extract_drug_name_node
from src.nodes.drug_info_node import fetch_drug_safety_node
from src.schemas.extraction import DrugNameExtraction

@patch("src.core.llm_factory.LLMFactory.get_llm")
def test_extract_drug_name_node_success(mock_get_llm):
    """Test that the agent successfully cleans a messy brand name input."""
    # Setup mocks
    mock_llm = MagicMock()
    mock_structured_llm = MagicMock()
    mock_get_llm.return_value = mock_llm
    mock_llm.with_structured_output.return_value = mock_structured_llm
    
    # Clinically accurate mock conversion: "lipitor 40 mg tab" -> "Lipitor"
    mock_result = DrugNameExtraction(standardized_name="Lipitor")
    mock_structured_llm.invoke.return_value = mock_result
    
    # Run node with matching raw input
    state: MedCheckerState = {
        "raw_input": "lipitor 40 mg tab",
        "extracted_drug_name": None,
        "safety_profile": None
    }
    
    output = extract_drug_name_node(state)
    
    # Assertions
    assert output == {"extracted_drug_name": "Lipitor"}
    mock_llm.with_structured_output.assert_called_once_with(DrugNameExtraction)


@patch("src.nodes.drug_info_node.get_drug_safety_info")
def test_fetch_drug_safety_node_success(mock_tool):
    """Test that the drug info node fetches and attaches safety data correctly."""
    # Setup mocks
    mock_tool.invoke.return_value = {
        "query_name": "Lipitor",
        "rxcuis": ["617314"],
        "ingredients": ["atorvastatin"],
        "safety_profiles": {
            "contraindications": ["Acute liver failure or decompensated cirrhosis"],
            "warnings_and_cautions": ["Myopathy and Rhabdomyolysis"]
        }
    }
    
    # Ensure state tracking remains logically consistent 
    state: MedCheckerState = {
        "raw_input": "lipitor 40 mg tab",
        "extracted_drug_name": "Lipitor",
        "safety_profile": None
    }
    
    output = fetch_drug_safety_node(state)
    
    # Assertions
    assert output["safety_profile"]["query_name"] == "Lipitor"
    assert "atorvastatin" in output["safety_profile"]["ingredients"]
    assert len(output["safety_profile"]["safety_profiles"]["contraindications"]) > 0
    mock_tool.invoke.assert_called_once_with({"drug_name": "Lipitor"})