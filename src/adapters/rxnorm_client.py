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

    def get_approximate_rxcuis(self, drug_name: str) -> List[str]:
        """
        Query RxNorm approximateTerm matching for a drug name (fuzzy spelling fallback).
        """
        try:
            response = self.session.get(f"{self.base_url}/approximateTerm.json", params={"term": drug_name, "maxEntries": 10})
            response.raise_for_status()
            data = response.json()
            candidates = data.get("approximateGroup", {}).get("candidate") or []
            rxcuis = {cand["rxcui"] for cand in candidates if cand.get("rxcui")}
            return sorted(list(rxcuis))
        except Exception:
            return []

    def get_rxcuis_by_name(self, drug_name: str) -> List[str]:
        """
        Query NLM RxNorm for a drug name and extract all product RxCUIs found.
        Falls back to approximate term matching if no direct matches are found.
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
            if rxcuis:
                return sorted(list(rxcuis))
        except Exception:
            pass

        # Fallback to approximate matching for fuzzy search/spelling errors
        return self.get_approximate_rxcuis(drug_name)

    def get_direct_rxcui(self, name: str) -> str:
        """
        Query findRxcuiByString to find a direct concept RxCUI.
        GET /rxcui.json?name={name}
        """
        try:
            response = self.session.get(f"{self.base_url}/rxcui.json", params={"name": name})
            response.raise_for_status()
            data = response.json()
            rxnorm_ids = data.get("idGroup", {}).get("rxnormId")
            if rxnorm_ids:
                return rxnorm_ids[0]
        except Exception:
            pass
        return None

    def get_concept_properties(self, rxcui: str) -> dict:
        """
        Retrieve properties of a concept RxCUI (including TTY).
        GET /rxcui/{rxcui}/properties.json
        """
        try:
            response = self.session.get(f"{self.base_url}/rxcui/{rxcui}/properties.json")
            response.raise_for_status()
            return response.json().get("properties") or {}
        except Exception:
            return {}

    def get_related_ingredients_for_rxcui(self, rxcui: str) -> List[str]:
        """
        Query related IN (Ingredient) concepts directly for a given RxCUI.
        """
        try:
            related_data = self.get_related_ingredients(rxcui)
            concept_groups = related_data.get("relatedGroup", {}).get("conceptGroup") or []
            ingredients = []
            for group in concept_groups:
                if group.get("tty") == "IN":
                    for prop in group.get("conceptProperties", []):
                        name = prop.get("name")
                        if name:
                            ingredients.append(name.lower())
            return ingredients
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
        Resolve a drug name to its active ingredients using a tiered strategy:
        1. Look for direct Rxcui. If found:
           - If it is an Ingredient (TTY = IN/PIN), return [ingredient_name].
           - If it is a Brand or Product (TTY = BN/SCD/SBD/etc.), get its direct related ingredients.
        2. If not found, check approximate matching. If an approximate candidate is an ingredient or product,
           resolve it directly.
        3. If all else fails, fallback to broad product aggregation search.
        """
        drug_name_clean = drug_name.strip()
        
        # 1. Direct concept mapping
        direct_rxcui = self.get_direct_rxcui(drug_name_clean)
        if direct_rxcui:
            props = self.get_concept_properties(direct_rxcui)
            tty = props.get("tty")
            concept_name = props.get("name", drug_name_clean)
            
            if tty in ("IN", "PIN"):
                return {
                    "rxcuis": [direct_rxcui],
                    "ingredients": [concept_name.lower()]
                }
            elif tty:
                ingredients = self.get_related_ingredients_for_rxcui(direct_rxcui)
                if ingredients:
                    return {
                        "rxcuis": [direct_rxcui],
                        "ingredients": sorted(list(set(ingredients)))
                    }
        
        # 2. Approximate matching fallback
        approx_rxcuis = self.get_approximate_rxcuis(drug_name_clean)
        if approx_rxcuis:
            best_approx = approx_rxcuis[0]
            props = self.get_concept_properties(best_approx)
            tty = props.get("tty")
            concept_name = props.get("name", drug_name_clean)
            
            if tty in ("IN", "PIN"):
                return {
                    "rxcuis": [best_approx],
                    "ingredients": [concept_name.lower()]
                }
            elif tty:
                ingredients = self.get_related_ingredients_for_rxcui(best_approx)
                if ingredients:
                    return {
                        "rxcuis": [best_approx],
                        "ingredients": sorted(list(set(ingredients)))
                    }
                    
        # 3. Broad aggregate fallback (old behavior)
        rxcuis = self.get_rxcuis_by_name(drug_name_clean)
        ingredients = self.get_ingredients_by_rxcuis(rxcuis)
        return {
            "rxcuis": rxcuis,
            "ingredients": ingredients
        }
