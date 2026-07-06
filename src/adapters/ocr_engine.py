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
    Returns list of (text, confidence) tuples.
    """
    result = get_ocr_engine().ocr(image, cls=True)

    if not result:
        return []

    extracted = []

    # PaddleOCR 3.x returns a different structure than 2.x
    # Handle both formats safely
    for item in result:
        if item is None:
            continue
        # 2.x format: list of [bbox, (text, confidence)]
        if isinstance(item, list):
            for line in item:
                if line and len(line) >= 2 and isinstance(line[1], tuple):
                    extracted.append(line)
        # 3.x format: dict with 'rec_texts' and 'rec_scores'
        elif isinstance(item, dict):
            texts = item.get("rec_texts", [])
            scores = item.get("rec_scores", [])
            for text, score in zip(texts, scores):
                extracted.append([None, (text, score)])

    return extracted