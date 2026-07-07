import requests
from typing import Optional
from src.schemas.drug_data import OpenFDALabelInfo

class OpenFDAClient:
    def __init__(self, base_url: str = "https://api.fda.gov/drug"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def get_label_by_ingredient(self, ingredient: str) -> Optional[OpenFDALabelInfo]:
        """
        Query OpenFDA drug label API by generic active ingredient name.
        GET /label.json?search=openfda.generic_name:"{ingredient}"&limit=1
        """
        try:
            response = self.session.get(
                f"{self.base_url}/label.json",
                params={
                    "search": f'openfda.generic_name:"{ingredient}"',
                    "limit": 1
                }
            )
            response.raise_for_status()
            data = response.json()
            results = data.get("results")
            if not results:
                return None
            
            return self._parse_label_data(results[0])
        except Exception:
            return None

    def _get_joined_text(self, label_data: dict, field_name: str) -> Optional[str]:
        """
        Helper to safely extract field values and join lists into multi-line strings.
        """
        val = label_data.get(field_name)
        if isinstance(val, list):
            return "\n".join(val)
        elif isinstance(val, str):
            return val
        return None

    def _parse_label_data(self, label_data: dict) -> OpenFDALabelInfo:
        """
        Parse raw label data dictionary from OpenFDA API into OpenFDALabelInfo.
        """
        # Fallback for warnings and cautions
        warnings_and_cautions = self._get_joined_text(label_data, "warnings_and_cautions")
        if not warnings_and_cautions:
            warnings_and_cautions = self._get_joined_text(label_data, "warnings")

        return OpenFDALabelInfo(
            contraindications=self._get_joined_text(label_data, "contraindications"),
            boxed_warning=self._get_joined_text(label_data, "boxed_warning"),
            warnings_and_cautions=warnings_and_cautions,
            pregnancy=self._get_joined_text(label_data, "pregnancy"),
            supplemental_patient_material=self._get_joined_text(label_data, "supplemental_patient_material"),
            drug_interactions=self._get_joined_text(label_data, "drug_interactions"),
            food_interactions=self._get_joined_text(label_data, "food_interactions")
        )
