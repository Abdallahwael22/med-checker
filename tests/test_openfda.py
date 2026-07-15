import pytest
from unittest.mock import MagicMock, patch
from src.adapters.openfda_client import OpenFDAClient
from src.tools.openfda_tool import fetch_drug_labels_from_openfda
from src.schemas.drug_data import OpenFDALabelInfo

def test_openfda_client_init():
    client = OpenFDAClient()
    assert client.base_url == "https://api.fda.gov/drug"

@patch("requests.Session.get")
def test_get_label_by_ingredient_success(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "results": [
            {
                "openfda": {
                    "generic_name": ["ATORVASTATIN CALCIUM"],
                    "brand_name": ["LIPITOR"],
                    "substance_name": ["ATORVASTATIN"]
                },
                "warnings": ["Do not use if pregnant."],
                "contraindications": ["Active liver disease."],
                "boxed_warning": ["WARNING: Severe liver risk."],
                "pregnancy": ["Pregnancy category X."],
                "drug_interactions": ["Avoid with cyclosporine."],
                "food_interactions": ["Avoid grapefruit juice."]
            }
        ]
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    client = OpenFDAClient()
    label = client.get_label_by_ingredient("atorvastatin")
    
    assert label is not None
    assert label.warnings_and_cautions == "Do not use if pregnant."
    assert label.contraindications == "Active liver disease."
    assert label.boxed_warning == "WARNING: Severe liver risk."
    assert label.pregnancy == "Pregnancy category X."
    assert label.drug_interactions == "Avoid with cyclosporine."
    assert label.food_interactions == "Avoid grapefruit juice."
    
    mock_get.assert_called_once_with(
        "https://api.fda.gov/drug/label.json",
        params={"search": 'openfda.generic_name:"atorvastatin"', "limit": 1}
    )

@patch("requests.Session.get")
def test_get_label_by_ingredient_not_found(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"results": []}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    client = OpenFDAClient()
    label = client.get_label_by_ingredient("unknown")
    assert label is None

@patch("src.adapters.openfda_client.OpenFDAClient.get_label_by_ingredient")
def test_fetch_drug_labels_from_openfda_tool(mock_get_label):
    mock_label = OpenFDALabelInfo(
        contraindications="Liver disease.",
        warnings_and_cautions="Use caution.",
        pregnancy="N/A",
        drug_interactions="Cyclosporine",
        food_interactions="Grapefruit juice"
    )
    
    # Return mock_label for atorvastatin, None for others
    def side_effect(ing):
        if ing == "atorvastatin":
            return mock_label
        return None
        
    mock_get_label.side_effect = side_effect
    
    result = fetch_drug_labels_from_openfda.invoke({"ingredients": ["atorvastatin", "unknown"]})
    
    assert "atorvastatin" in result
    assert "unknown" in result
    assert result["unknown"] is None
    assert result["atorvastatin"] == mock_label.model_dump()
    assert result["atorvastatin"]["contraindications"] == "Liver disease."
