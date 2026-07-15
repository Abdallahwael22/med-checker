# pyrefly: ignore [missing-import]
import pytest
from unittest.mock import patch, MagicMock
# pyrefly: ignore [missing-import]
from src.tools.drug_safety_tool import get_drug_safety_info
# pyrefly: ignore [missing-import]
from src.schemas.drug_data import OpenFDALabelInfo

@patch("src.adapters.rxnorm_client.RxNormClient.extract_ingredients")
@patch("src.adapters.openfda_client.OpenFDAClient.get_label_by_ingredient")
def test_get_drug_safety_info_tool(mock_get_label, mock_extract):
    # Setup mocks
    mock_extract.return_value = {
        "rxcuis": ["617314"],
        "ingredients": ["atorvastatin"]
    }
    
    mock_label = OpenFDALabelInfo(
        contraindications="Liver issues.",
        warnings_and_cautions="Be careful.",
        pregnancy="Do not use.",
        drug_interactions="Avoid cyclosporine.",
        food_interactions="Avoid grapefruit juice."
    )
    mock_get_label.return_value = mock_label

    # Invoke tool
    result = get_drug_safety_info.invoke({"drug_name": "Lipitor"})

    # Asserts
    assert result["query_name"] == "Lipitor"
    assert result["rxcuis"] == ["617314"]
    assert result["ingredients"] == ["atorvastatin"]
    assert "atorvastatin" in result["safety_profiles"]
    assert result["safety_profiles"]["atorvastatin"] == mock_label.model_dump()
    
    mock_extract.assert_called_once_with("Lipitor")
    mock_get_label.assert_called_once_with("atorvastatin")
