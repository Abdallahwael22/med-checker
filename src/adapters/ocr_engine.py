from paddleocr import PaddleOCR
import numpy as np

_engine = None


def get_ocr_engine() -> PaddleOCR:
    global _engine
    if _engine is None:
        _engine = PaddleOCR(
            use_angle_cls=True,
            lang="en"
        )
    return _engine


def run_paddleocr(image: np.ndarray) -> list:
    """
    Run PaddleOCR on a preprocessed image.
    Returns list of [bbox, (text, confidence)] per detected region.
    """
    result = get_ocr_engine().ocr(image, cls=True)
    return result[0] if result and result[0] else []