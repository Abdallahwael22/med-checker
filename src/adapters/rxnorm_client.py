import requests
from typing import List

class RxNormClient:
    def __init__(self, base_url: str = "https://rxnav.nlm.nih.gov/REST"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def get_drugs(self, name: str) -> dict:
        """
        Query drugs by name.
        GET /drugs.json?name={name}
        """
        response = self.session.get(f"{self.base_url}/drugs.json", params={"name": name})
        response.raise_for_status()
        return response.json()

    def get_related_ingredients(self, rxcui: str) -> dict:
        """
        Query related concepts of type IN (Ingredient) for a given RxCUI.
        GET /rxcui/{rxcui}/related.json?tty=IN
        """
        response = self.session.get(f"{self.base_url}/rxcui/{rxcui}/related.json", params={"tty": "IN"})
        response.raise_for_status()
        return response.json()

    def get_rxcuis_by_name(self, drug_name: str) -> List[str]:
        """
        Query NLM RxNorm for a drug name and extract all product RxCUIs found.
        """
        try:
            data = self.get_drugs(drug_name)
            concept_groups = data.get("drugGroup", {}).get("conceptGroup") or []
            rxcuis = {
                prop["rxcui"]
                for group in concept_groups
                for prop in group.get("conceptProperties", [])
                if prop.get("rxcui")
            }
            return sorted(list(rxcuis))
        except Exception:
            return []

    def get_ingredients_by_rxcuis(self, rxcuis: List[str]) -> List[str]:
        """
        For each product RxCUI, fetch the related active ingredients (tty=IN)
        and return the sorted list of unique normalized ingredient names.
        """
        ingredients = set()
        for rxcui in rxcuis:
            try:
                related_data = self.get_related_ingredients(rxcui)
                concept_groups = related_data.get("relatedGroup", {}).get("conceptGroup") or []
                for group in concept_groups:
                    if group.get("tty") == "IN":
                        for prop in group.get("conceptProperties", []):
                            name = prop.get("name")
                            if name:
                                ingredients.add(name.lower())
            except Exception:
                continue
        return sorted(list(ingredients))

    def extract_ingredients(self, drug_name: str) -> dict:
        """
        Resolve a drug name to its active ingredients by first resolving product RxCUIs,
        then querying related active ingredient concepts.
        
        Returns a dict: {"rxcuis": list[str], "ingredients": list[str]}
        """
        rxcuis = self.get_rxcuis_by_name(drug_name)
        ingredients = self.get_ingredients_by_rxcuis(rxcuis)
        return {
            "rxcuis": rxcuis,
            "ingredients": ingredients
        }
