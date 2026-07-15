import pytest
from src.nodes.ocr_node import ocr_node, compute_confidence
from src.state import MedCheckerState


def make_state(image_path: str) -> MedCheckerState:
    with open(image_path, "rb") as f:
        return {
            "raw_image": f.read(),
            "patient_id": "patient_001",
            "ocr": None,
            "agent": None,
            "reasoning": None,
            "audit_log": {}
        }


# ── Unit tests (no real image needed) ──

def test_compute_confidence_empty():
    assert compute_confidence([]) == 0.0


def test_compute_confidence_uses_minimum():
    fake = [
        [None, ("drug name", 0.95)],
        [None, ("5 mg", 0.45)],
        [None, ("tablets", 0.98)],
    ]
    assert compute_confidence(fake) == 0.45


def test_compute_confidence_single():
    fake = [[None, ("melatonin", 0.92)]]
    assert compute_confidence(fake) == 0.92


# ── Integration tests (need real images) ──

def test_clean_label_passes():
    state = make_state("data/samples/melatonin_clean.jpg")
    result = ocr_node(state)

    assert result["ocr"] is not None
    assert result["ocr"].scanned_drug_name == "melatonin"
    assert "mg" in result["ocr"].scanned_dosage
    assert result["ocr"].ocr_confidence >= 0.75
    assert result["ocr"].ocr_needs_review is False


def test_blurry_label_sets_review_flag():
    state = make_state("data/samples/blurry_label.jpg")
    result = ocr_node(state)

    assert result["ocr"].ocr_needs_review is True
    assert result["ocr"].scanned_drug_name == ""


def test_retry_count_increments():
    state = make_state("data/samples/blurry_label.jpg")
    result = ocr_node(state)

    assert result["ocr"].ocr_retry_count > 0


def test_ocr_never_crashes_on_bad_image():
    """Even garbage bytes should not raise — just set review flag."""
    state = {
        "raw_image": b"this_is_not_an_image",
        "patient_id": "patient_001",
        "ocr": None, "agent": None, "reasoning": None,
        "audit_log": {}
    }
    try:
        result = ocr_node(state)
        assert result["ocr"].ocr_needs_review is True
    except Exception as e:
        pytest.fail(f"ocr_node raised unexpectedly: {e}")


def test_confidence_always_between_zero_and_one():
    state = make_state("data/samples/melatonin_clean.jpg")
    result = ocr_node(state)
    assert 0.0 <= result["ocr"].ocr_confidence <= 1.0