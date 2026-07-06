# run this as a one-off script: python scripts/check_preprocessing.py
import cv2
import numpy as np

from src.nodes.preprocessing import decode_image, basic_preprocess, aggressive_preprocess

with open("data/samples/clean_label.jpg", "rb") as f:
    img_bytes = f.read()

img = decode_image(img_bytes)
basic = basic_preprocess(img)
aggressive = aggressive_preprocess(img)

cv2.imwrite("data/samples/debug_basic.jpg", basic)
cv2.imwrite("data/samples/debug_aggressive.jpg", aggressive)
print("Check data/samples/ for debug images")

# Basic should be grayscale (2D array, not 3D)
assert len(basic.shape) == 2, "basic should be grayscale"

# Aggressive should be pure black and white (only 0 and 255)
unique_values = np.unique(aggressive)
assert set(unique_values).issubset({0, 255}), "aggressive should be binary"

# Neither should be empty
assert basic.size > 0
assert aggressive.size > 0

print("✅ basic is grayscale")
print("✅ aggressive is pure black and white")
print("✅ neither image is empty")
print(f"   original shape : {img.shape}")
print(f"   basic shape    : {basic.shape}")
print(f"   aggressive shape: {aggressive.shape}")