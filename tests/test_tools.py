import pytest
from unittest.mock import patch
from src.tools.rxnorm_tool import extract_drug_ingredients

@patch("src.adapters.rxnorm_client.RxNormClient.extract_ingredients")
def test_extract_drug_ingredients_tool(mock_extract):
    mock_extract.return_value = {
        "rxcuis": ["617314"],
        "ingredients": ["atorvastatin"]
    }
    
    result = extract_drug_ingredients.invoke({"drug_name": "Lipitor"})
    
    assert result == {
        "query_name": "Lipitor",
        "rxcuis": ["617314"],
        "ingredients": ["atorvastatin"]
    }
    mock_extract.assert_called_once_with("Lipitor")
