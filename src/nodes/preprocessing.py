import cv2
import numpy as np


def decode_image(image_bytes: bytes) -> np.ndarray:
    """Convert raw bytes to an OpenCV image array."""
    # The problem this function solves:
    # - The image arrives from Streamlit as raw bytes (bytes object)
    # - OpenCV and PaddleOCR can't work with raw bytes directly, they need a numpy array to process images.
    # - This function converts the bytes to a numpy array.
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image bytes")
    return img


def basic_preprocess(img: np.ndarray) -> np.ndarray:
    """
    Light preprocessing for first OCR attempt.
    Grayscale + contrast + sharpen.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)    # Convert the image to grayscale
    gray = cv2.equalizeHist(gray)                   # Equalize the histogram of the grayscale image to improve contrast
    kernel = np.array([[0, -1, 0],                  # Sharpen the image
                       [-1,  5, -1],
                       [0, -1, 0]])
    return cv2.filter2D(gray, -1, kernel)           # Apply the kernel to the grayscale image


def aggressive_preprocess(img: np.ndarray) -> np.ndarray:
    """
    Heavy preprocessing for retry attempts.
    Denoise + Otsu threshold.
    """
    # The problem this function solves:
    # - The image may contain noise or artifacts that can affect the OCR results.
    # - This function denoises the image to improve the quality of the image.

    # Denoise the image using the fastNlMeansDenoisingColored function
    # The numbers 10, 10, 7, 21 control how aggressively it smooths — higher = more smoothing but slower.
    denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
    gray = cv2.cvtColor(denoised, cv2.COLOR_BGR2GRAY)

    
    _, thresh = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    # This converts the grayscale image into a pure black and white image — 
    # every pixel becomes either 0 (black) or 255 (white), nothing in between.

    # Otsu's algorithm automatically finds the best threshold value by analyzing the histogram of the image. 
    # It asks: "what value best separates text from background?" and applies that value.

    # The result: text becomes pure black, background becomes pure white. 
    # This is the clearest possible input for OCR.

    return thresh


def deskew(img: np.ndarray) -> np.ndarray:
    """
    Correct image rotation if the label is tilted.
    Works on both color and grayscale images.
    """
    # Work on grayscale for coordinate detection
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img.copy()

    # Invert image if background is light (i.e. mean pixel value is > 127)
    # so that text becomes bright (high value) and background becomes black (0).
    if np.mean(gray) > 127:
        gray = cv2.bitwise_not(gray)

    # Threshold to isolate text foreground from background noise
    _, gray_thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)

    # Step A — Find all bright pixels (which are now text foreground pixels)
    coords = np.column_stack(np.where(gray_thresh > 0))
    if len(coords) < 5:
        return img  # not enough points to compute angle

    # Step B — Compute angle
    angle = cv2.minAreaRect(coords)[-1]

    # Step C — Adjust angle
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    # Only apply rotation if there is a significant skew to avoid rotating
    # perfectly aligned images by a small fraction of a degree.
    if abs(angle) < 1.0 or abs(angle) > 89.0:
        return img

    (h, w) = img.shape[:2]

    # Step D — Rotate the image
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    return cv2.warpAffine(img, M, (w, h))

# Summary of the preprocessing functions:

    # First attempt — light processing
        # img = decode_image(state["raw_image"])      # bytes → numpy
        # processed = basic_preprocess(img)           # grayscale + contrast + sharpen
        # processed = deskew(processed)              # straighten
        # raw = run_paddleocr(processed)             # run OCR
        # confidence = compute_confidence(raw)       # check result

    # if confidence < 0.75:
    #     # Second attempt — heavy processing
    #     processed = aggressive_preprocess(img)  # denoise + threshold
    #     processed = deskew(processed)          # straighten
    #     raw = run_paddleocr(processed)         # run OCR again
