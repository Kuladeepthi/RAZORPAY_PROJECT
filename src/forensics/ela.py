"""
SentinelEvidence — Format-Aware Error Level Analysis (ELA)

Analyzes local compression error differences across image regions for lossy formats (JPEG).
On native lossless PNG screenshots (standard for Android/iOS UPI confirmation screens),
JPEG ELA is safely bypassed to avoid domain-mismatch false positives from vector font rendering,
relying instead on Regional Copy-Move, Edge Discontinuities, and Ledger Reconciliation.
"""

import io
from typing import Tuple, Union
import numpy as np
import cv2
from PIL import Image


def error_level_analysis(
    image_input: Union[str, np.ndarray, Image.Image],
    quality: int = 90,
    scale: int = 15,
    is_png: bool = False
) -> Tuple[np.ndarray, float, np.ndarray]:
    """
    Computes Error Level Analysis on lossy JPEG document uploads.
    Returns (ela_image, ela_score, outlier_mask).
    """
    if isinstance(image_input, str):
        if image_input.lower().endswith(".png"):
            is_png = True
        pil_img = Image.open(image_input).convert("RGB")
    elif isinstance(image_input, np.ndarray):
        if len(image_input.shape) == 2:
            pil_img = Image.fromarray(image_input).convert("RGB")
        elif image_input.shape[2] == 4:
            pil_img = Image.fromarray(cv2.cvtColor(image_input, cv2.COLOR_BGRA2RGB))
            is_png = True
        else:
            pil_img = Image.fromarray(cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB))
    elif isinstance(image_input, Image.Image):
        if getattr(image_input, "format", None) in ["PNG", "BMP", "TIFF"]:
            is_png = True
        pil_img = image_input.convert("RGB")
    else:
        raise ValueError(f"Unsupported image input type: {type(image_input)}")

    w, h = pil_img.size

    # Compute Error Level Analysis recompression difference
    buffer = io.BytesIO()
    pil_img.save(buffer, "JPEG", quality=quality)
    buffer.seek(0)
    recompressed = Image.open(buffer)

    original_arr = np.asarray(pil_img, dtype=np.int16)
    recomp_arr = np.asarray(recompressed, dtype=np.int16)

    diff = np.abs(original_arr - recomp_arr).astype(np.uint8)
    ela_image = np.clip(diff * scale, 0, 255).astype(np.uint8)

    # On native lossless PNG screenshots, ELA score is safely 0.0 to prevent
    # sub-pixel font false alarms, while ela_image visualizes clean compression delta
    if is_png:
        blank_mask = np.zeros((h, w), dtype=np.uint8)
        return ela_image, 0.0, blank_mask

    gray_diff = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY).astype(np.float32)

    patch_size = 32
    text_patches = []

    for y in range(0, h - patch_size, patch_size):
        for x in range(0, w - patch_size, patch_size):
            patch = gray_diff[y : y + patch_size, x : x + patch_size]
            m = float(np.mean(patch))
            if m > 3.0:
                text_patches.append(m)

    if len(text_patches) < 6:
        return ela_image, 0.0, np.zeros_like(gray_diff, dtype=np.uint8)

    text_patches_arr = np.array(text_patches)
    med = float(np.median(text_patches_arr))
    mad = float(np.median(np.abs(text_patches_arr - med))) + 1e-4

    outlier_count = sum(1 for p in text_patches if p > (med + 3.5 * mad))
    outlier_ratio = outlier_count / float(len(text_patches))

    pixel_thresh = med + 3.5 * mad
    outlier_mask = (gray_diff > pixel_thresh).astype(np.uint8) * 255

    score = float(np.clip(outlier_ratio * 4.0, 0.0, 1.0))
    return ela_image, score, outlier_mask
