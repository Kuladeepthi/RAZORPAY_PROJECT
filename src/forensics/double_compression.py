"""
SentinelEvidence — Forensic Signal 3: DCT Double JPEG Quantization Detector

Measures Discrete Cosine Transform (DCT) AC coefficient histogram periodicity.
When an image is edited and re-compressed as JPEG, the primary quantization
grid interacts with the secondary compression grid, inducing comb-like periodic peaks.
"""

from typing import Tuple, Union
import numpy as np
import cv2
from PIL import Image


def detect_double_compression(
    image_input: Union[str, np.ndarray, Image.Image],
    block_size: int = 8,
    num_bins: int = 64
) -> Tuple[float, np.ndarray]:
    """
    Computes double-JPEG compression periodicity score via DCT histogram autocorrelation.
    """
    if isinstance(image_input, str):
        img_gray = cv2.imread(image_input, cv2.IMREAD_GRAYSCALE)
        if img_gray is None:
            raise FileNotFoundError(f"Could not load image from {image_input}")
    elif isinstance(image_input, Image.Image):
        img_gray = np.array(image_input.convert("L"))
    elif isinstance(image_input, np.ndarray):
        if len(image_input.shape) == 3:
            img_gray = cv2.cvtColor(image_input, cv2.COLOR_BGR2GRAY)
        else:
            img_gray = image_input.copy()
    else:
        raise ValueError(f"Unsupported image input type: {type(image_input)}")

    h, w = img_gray.shape
    h_crop = h - (h % block_size)
    w_crop = w - (w % block_size)

    if h_crop < block_size * 4 or w_crop < block_size * 4:
        return 0.0, np.zeros(num_bins)

    img_blocks = img_gray[:h_crop, :w_crop].astype(np.float32) - 128.0

    ac_coefficients = []
    for y in range(0, h_crop, block_size):
        for x in range(0, w_crop, block_size):
            block = img_blocks[y : y + block_size, x : x + block_size]
            dct_block = cv2.dct(block)
            # Low-frequency AC components (0,1) and (1,0)
            ac_coefficients.append(dct_block[0, 1])
            ac_coefficients.append(dct_block[1, 0])

    if not ac_coefficients:
        return 0.0, np.zeros(num_bins)

    ac_arr = np.clip(np.array(ac_coefficients, dtype=np.float32), -32.0, 32.0)
    hist, _ = np.histogram(ac_arr, bins=num_bins, range=(-32.0, 32.0))
    hist = hist / (float(hist.sum()) + 1e-7)

    # Autocorrelation of the histogram to find repeating harmonic periods
    autocorr = np.correlate(hist - np.mean(hist), hist - np.mean(hist), mode='full')
    autocorr = autocorr[len(autocorr)//2:]  # Take positive lags

    # Periodicity check: peak in lag 2 to 10 relative to zero-lag
    if len(autocorr) > 12 and autocorr[0] > 1e-6:
        normalized_lags = autocorr[2:12] / autocorr[0]
        max_harmonic_peak = float(np.max(normalized_lags))
        # High secondary harmonic peak indicates periodic quantization comb
        score = float(np.clip((max_harmonic_peak - 0.25) * 2.0, 0.0, 1.0))
    else:
        score = 0.0

    return score, hist
