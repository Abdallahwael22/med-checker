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
        Helper to safely extract field values, join lists, and normalize carriage returns.
        """
        val = label_data.get(field_name)
        if isinstance(val, list):
            joined = "\n".join(val)
        elif isinstance(val, str):
            joined = val
        else:
            return None
            
        # Normalize carriage returns to prevent terminal printing issues
        return joined.replace("\r\n", "\n").replace("\r", "\n")


    def _parse_label_data(self, label_data: dict) -> OpenFDALabelInfo:
        """
        Parse raw label data dictionary from OpenFDA API into OpenFDALabelInfo.
        Supports fallbacks for OTC (Over-the-Counter) drugs.
        """
        # Assemble comprehensive warnings and cautions for OTC/Rx labels
        warnings_sections = []
        
        main_warnings = self._get_joined_text(label_data, "warnings_and_cautions")
        if not main_warnings:
            main_warnings = self._get_joined_text(label_data, "warnings")
        if main_warnings:
            warnings_sections.append(main_warnings)
            
        # Append extra safety warnings if present (typical in OTC labels)
        for field in ["ask_doctor", "when_using", "stop_use", "precautions", "general_precautions"]:
            val = self._get_joined_text(label_data, field)
            if val:
                # Format nicely with a markdown subheader
                header = field.replace("_", " ").title()
                warnings_sections.append(f"### {header}\n{val}")
                
        warnings_and_cautions = "\n\n".join(warnings_sections) if warnings_sections else None

        # Fallback for contraindications (OTC drugs use 'do_not_use')
        contraindications = self._get_joined_text(label_data, "contraindications")
        if not contraindications:
            contraindications = self._get_joined_text(label_data, "do_not_use")

        # Fallback for pregnancy (OTC drugs use 'pregnancy_or_breast_feeding')
        pregnancy = self._get_joined_text(label_data, "pregnancy")
        if not pregnancy:
            pregnancy = self._get_joined_text(label_data, "pregnancy_or_breast_feeding")

        # Fallback for drug interactions (OTC drugs use 'ask_doctor_or_pharmacist')
        drug_interactions = self._get_joined_text(label_data, "drug_interactions")
        if not drug_interactions:
            drug_interactions = self._get_joined_text(label_data, "ask_doctor_or_pharmacist")

        return OpenFDALabelInfo(
            contraindications=contraindications,
            boxed_warning=self._get_joined_text(label_data, "boxed_warning"),
            warnings_and_cautions=warnings_and_cautions,
            pregnancy=pregnancy,
            supplemental_patient_material=self._get_joined_text(label_data, "supplemental_patient_material"),
            drug_interactions=drug_interactions,
            food_interactions=self._get_joined_text(label_data, "food_interactions")
        )



