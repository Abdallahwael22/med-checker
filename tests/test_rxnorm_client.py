import pytest
from unittest.mock import MagicMock, patch
from src.adapters.rxnorm_client import RxNormClient
from src.schemas.drug_data import DrugIngredientInfo

def test_rxnorm_client_init():
    client = RxNormClient()
    assert client.base_url == "https://rxnav.nlm.nih.gov/REST"

@patch("requests.Session.get")
def test_get_drugs(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"drugGroup": {"name": "Lipitor"}}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    client = RxNormClient()
    res = client.get_drugs("Lipitor")
    assert res == {"drugGroup": {"name": "Lipitor"}}
    mock_get.assert_called_once_with("https://rxnav.nlm.nih.gov/REST/drugs.json", params={"name": "Lipitor"})

@patch("requests.Session.get")
def test_get_related_ingredients(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"relatedGroup": {"conceptGroup": []}}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    client = RxNormClient()
    res = client.get_related_ingredients("617314")
    assert res == {"relatedGroup": {"conceptGroup": []}}
    mock_get.assert_called_once_with("https://rxnav.nlm.nih.gov/REST/rxcui/617314/related.json", params={"tty": "IN"})

def test_get_rxcuis_by_name():
    client = RxNormClient()
    client.get_drugs = MagicMock(return_value={
        "drugGroup": {
            "name": None,
            "conceptGroup": [
                {
                    "tty": "SBD",
                    "conceptProperties": [
                        {"rxcui": "617314", "name": "Lipitor 10 MG"},
                        {"rxcui": "617318", "name": "Lipitor 20 MG"}
                    ]
                }
            ]
        }
    })
    
    rxcuis = client.get_rxcuis_by_name("Lipitor")
    assert rxcuis == ["617314", "617318"]
    client.get_drugs.assert_called_once_with("Lipitor")

def test_get_ingredients_by_rxcuis():
    client = RxNormClient()
    
    # Mock get_related_ingredients for different inputs
    def mock_related(rxcui):
        if rxcui == "617314":
            return {
                "relatedGroup": {
                    "conceptGroup": [
                        {
                            "tty": "IN",
                            "conceptProperties": [
                                {"rxcui": "83367", "name": "Atorvastatin"}
                            ]
                        }
                    ]
                }
            }
        return {"relatedGroup": {"conceptGroup": []}}
        
    client.get_related_ingredients = MagicMock(side_effect=mock_related)
    
    ingredients = client.get_ingredients_by_rxcuis(["617314", "invalid"])
    assert ingredients == ["atorvastatin"]

def test_extract_ingredients():
    client = RxNormClient()
    client.get_rxcuis_by_name = MagicMock(return_value=["617314"])
    client.get_ingredients_by_rxcuis = MagicMock(return_value=["atorvastatin"])
    
    info = client.extract_ingredients("Lipitor")
    assert isinstance(info, DrugIngredientInfo)
    assert info.query_name == "Lipitor"
    assert info.rxcuis == ["617314"]
    assert info.ingredients == ["atorvastatin"]
