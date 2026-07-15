from src.schemas.extraction import ExtractedLabel
from src.schemas.state_sections import OCRSection


def test_extracted_label_valid():
    label = ExtractedLabel(
        drug_name="Melatonin",
        dosage="5",
        dosage_unit="mg",
        confidence=0.94
    )
    assert label.drug_name == "melatonin"   # validator lowercases it
    assert label.dosage_unit == "mg"
    assert label.confidence == 0.94


def test_extracted_label_empty_name_raises():
    try:
        ExtractedLabel(
            drug_name="   ",
            dosage="5",
            dosage_unit="mg",
            confidence=0.94
        )
        assert False, "should have raised"
    except Exception:
        pass


def test_ocr_section_defaults():
    section = OCRSection()
    assert section.scanned_drug_name == ""
    assert section.ocr_needs_review is False
    assert section.ocr_confidence == 0.0


def test_ocr_section_with_values():
    section = OCRSection(
        scanned_drug_name="melatonin",
        scanned_dosage="5mg",
        ocr_confidence=0.94,
        ocr_needs_review=False,
        ocr_retry_count=0
    )
    assert section.scanned_drug_name == "melatonin"
    assert section.ocr_confidence == 0.94