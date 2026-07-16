import os
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
            use_textline_orientation=True
        )
    return _engine


def run_paddleocr(image: np.ndarray) -> list:
    """
    Run PaddleOCR 3.x on a preprocessed image.
    Returns list of [None, (text, confidence)] per detected region.
    """
    # PaddleOCR 3.x requires 3-channel BGR image
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    result = get_ocr_engine().predict(image)  # use predict(), not ocr()

    if not result:
        return []

    extracted = []
    for item in result:
        if item is None:
            continue
        if isinstance(item, dict):
            texts = item.get("rec_texts", [])
            scores = item.get("rec_scores", [])
            for text, score in zip(texts, scores):
                extracted.append([None, (text, score)])

    return extracted