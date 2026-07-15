from src.state import MedCheckerState
from src.core.llm_factory import LLMFactory
from src.schemas.extraction import DrugNameExtraction

def extract_drug_name_node(state: MedCheckerState) -> dict:
    """
    Node that extracts a standardized drug name from the raw user input.
    """
    raw_input = state.get("raw_input", "")
    if not raw_input:
        return {"extracted_drug_name": None}
        
    llm = LLMFactory.get_llm()
    structured_llm = llm.with_structured_output(DrugNameExtraction)
    
    prompt = f"""You are a strict data-cleaning function for a medical API pipeline. Your task is to clean up raw human drug entries into clean, standardized brand or generic strings. 

### General Instructions & Rules:
1. SPELLING CORRECTION: Fix all spelling errors, typos, and misplaced letters using contextual medical knowledge (e.g., "strenth" -> "Strength").
2. NOISE STRIPPING: Strip away all trailing descriptors regarding dosage forms (e.g., "capsules", "pills", "ORAL TAB", "liquid-gels", "chewables").
3. STRENGTH REMOVAL: Strip away numerical metric strengths (e.g., "500mg", "20 MG", "25") unless it is an inseparable part of a specific brand name formulation (like "Extra Strength").
4. ACRONYM EXPANSION: Convert common human shorthand, abbreviations, or clinical acronyms into their full, official clinical brand or generic names (e.g., "Amox" -> "Amoxicillin").
5. STANDARDIZE DELIMITERS: Retain necessary clinical hyphens or spaces required by drug registries, but drop conversational text.
6. COMPACT OUTPUT: Output ONLY the final cleaned string. Do not include any punctuation, conversational introductory words, Markdown formatting, or bullet points.

### Examples:
Input: "tylenol extra strenth" -> Output: "Tylenol Extra Strength"
Input: "Lisinopril 20 MG ORAL TAB" -> Output: "Lisinopril"
Input: "Amox 500mg" -> Output: "Amoxicillin"
Input: "HCTZ 25" -> Output: "Hydrochlorothiazide"
Input: "advil liquid-gels" -> Output: "Advil"

Now, clean the following input.

Input: "{raw_input}"
Output:"""
    result = structured_llm.invoke(prompt)
    
    return {"extracted_drug_name": result.standardized_name}
