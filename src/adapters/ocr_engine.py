import os
# Disable mkldnn to prevent the ConvertPirAttribute2RuntimeAttribute NotImplementedError
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "0"

from paddleocr import PaddleOCR
import numpy as np
import cv2

_engine = None


def get_ocr_engine() -> PaddleOCR:
    global _engine
    if _engine is None:
        _engine = PaddleOCR(
            use_textline_orientation=True,
            lang="en",
            enable_mkldnn=False,
        )
    return _engine


def run_paddleocr(image: np.ndarray) -> list:
    """
    Run PaddleOCR on a preprocessed image.
    Supports both PaddleOCR 2.x and 3.x result structures.
    Returns list of [bbox, (text, confidence)] per detected region.
    """
    # PaddleOCR 3.x models (like UVDoc and Normalize) expect a 3-channel BGR/RGB image.
    # If the preprocessed image is grayscale, convert it to 3 channels to avoid tuple indexing errors.
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    result = get_ocr_engine().ocr(image)
    if not result:
        return []

    # PaddleOCR 3.x returns a list of dictionaries containing 'rec_texts' and 'rec_scores'
    if isinstance(result[0], dict):
        page = result[0]
        rec_texts = page.get("rec_texts", [])
        rec_scores = page.get("rec_scores", [])
        return [[None, (text, score)] for text, score in zip(rec_texts, rec_scores)]

    # PaddleOCR 2.x returns list of [bbox, (text, confidence)]
    if isinstance(result[0], list):
        return result[0]

    return []