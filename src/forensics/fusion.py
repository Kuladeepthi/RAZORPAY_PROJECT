"""
SentinelEvidence — High-Fidelity Forensic Fusion Engine (Calibrated Distribution)

Normalized output distribution:
- Authentic clean receipts: ~ 0.05 to 0.28 (Target: 80%+ Seamless ACCEPT)
- Ambiguous / noisy receipts: ~ 0.30 to 0.55 (ABSTAIN -> Safe Human Review)
- Definite forgeries (splicing, cloned stamps, heavy ELA): ~ 0.60 to 0.95 (REJECT -> Instant Block)
"""

from typing import Dict, Any, Union
import numpy as np
import cv2
from PIL import Image

from .ela import error_level_analysis
from .copy_move import detect_copy_move
from .double_compression import detect_double_compression


def generate_tamper_heatmap(
    original_bgr: np.ndarray,
    ela_mask: np.ndarray,
    copy_move_clusters: list,
    alpha: float = 0.70
) -> np.ndarray:
    """
    Generates an informative, localized thermal tamper heatmap overlay.
    - Authentic / near-zero tamper regions remain 100% untinted, crisp, and readable (zero purple hue).
    - Only anomalous localized regions (ELA outlier residuals, copy-move duplicated patches)
      render as warm thermal hotspots (yellow -> orange -> red) scaled to anomaly intensity.
    """
    h, w = original_bgr.shape[:2]
    density_map = np.zeros((h, w), dtype=np.float32)

    # 1. Incorporate localized ELA Outliers if present
    if ela_mask is not None and ela_mask.size > 0:
        ela_resized = cv2.resize(ela_mask, (w, h))
        ela_norm = ela_resized.astype(np.float32) / 255.0
        # Suppress ambient compression noise below 0.15
        ela_filtered = np.where(ela_norm > 0.15, ela_norm, 0.0)
        density_map += ela_filtered * 0.85

    # 2. Incorporate localized Copy-Move Cloned Region Coordinates
    for cluster in copy_move_clusters:
        p1 = cluster.get("src_point")
        p2 = cluster.get("dst_point")
        if p1:
            cv2.circle(density_map, (int(p1[0]), int(p1[1])), 28, 1.0, -1)
        if p2:
            cv2.circle(density_map, (int(p2[0]), int(p2[1])), 28, 1.0, -1)

    # 3. Smooth with Gaussian kernel to produce clean thermal halos around suspicious patches
    blurred = cv2.GaussianBlur(density_map, (35, 35), 0)
    blurred = np.clip(blurred, 0.0, 1.0)

    # 4. Suppress near-zero background noise so genuine documents stay 100% untinted
    hotspot_intensity = np.clip((blurred - 0.06) / 0.94, 0.0, 1.0)

    # 5. Apply COLORMAP_JET to generate the thermal spectrum
    density_uint8 = (blurred * 255).astype(np.uint8)
    color_heat = cv2.applyColorMap(density_uint8, cv2.COLORMAP_JET)

    # 6. Dynamic Local Alpha Blending:
    # On genuine regions (hotspot_intensity == 0.0), alpha is 0.0 (100% original document).
    # On suspicious regions (hotspot_intensity > 0.0), alpha smoothly scales up to 0.70.
    local_alpha = (hotspot_intensity * alpha).astype(np.float32)
    local_alpha_3ch = np.dstack([local_alpha, local_alpha, local_alpha])

    blended = (original_bgr.astype(np.float32) * (1.0 - local_alpha_3ch) + 
               color_heat.astype(np.float32) * local_alpha_3ch)

    return np.clip(blended, 0, 255).astype(np.uint8)


def fuse_forensic_signals(
    ela_score: float,
    copy_move_score: float,
    double_compression_score: float
) -> float:
    """
    Calibrated soft-max fusion that keeps clean documents firmly in the <0.30 band
    while escalating definitively on confirmed localized tampering.
    """
    # Max localized primary evidence
    max_ev = max(ela_score, copy_move_score)
    
    if max_ev > 0.60:
        # Strong local tamper signal (confirmed cloned stamp or high ELA outlier)
        fused = max_ev * 0.85 + (double_compression_score * 0.15)
    elif max_ev > 0.30:
        # Moderate anomaly (candidate for human review)
        fused = max_ev * 0.75 + (ela_score * 0.15) + (double_compression_score * 0.10)
    else:
        # Clean baseline document
        fused = (ela_score * 0.40) + (copy_move_score * 0.40) + (double_compression_score * 0.20)
        
    return float(np.clip(fused, 0.0, 1.0))


def run_forensic_pipeline(
    image_input: Union[str, np.ndarray, Image.Image]
) -> Dict[str, Any]:
    if isinstance(image_input, str):
        img_bgr = cv2.imread(image_input)
        if img_bgr is None:
            raise FileNotFoundError(f"Cannot read image from {image_input}")
    elif isinstance(image_input, Image.Image):
        img_bgr = cv2.cvtColor(np.array(image_input.convert("RGB")), cv2.COLOR_RGB2BGR)
    elif isinstance(image_input, np.ndarray):
        img_bgr = image_input.copy()
        if len(img_bgr.shape) == 2:
            img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_GRAY2BGR)
    else:
        raise ValueError(f"Unsupported input type: {type(image_input)}")

    # 1. ELA (Format-aware)
    ela_img, ela_score, ela_mask = error_level_analysis(image_input)

    # 2. Regional Patch Copy-Move (NCC)
    cm_overlay, cm_score, cm_clusters = detect_copy_move(img_bgr)

    # 3. Double-JPEG DCT Periodicity
    dc_score, _ = detect_double_compression(img_bgr)

    # Fused Score
    tamper_score = fuse_forensic_signals(ela_score, cm_score, dc_score)

    heatmap_overlay = generate_tamper_heatmap(img_bgr, ela_mask, cm_clusters)

    diagnostics = []
    if cm_score > 0.35:
        diagnostics.append(f"Cloned region/stamp detected ({len(cm_clusters)} matched patches, NCC >= 0.88)")
    if ela_score > 0.35:
        diagnostics.append(f"Compression error variance elevated (ELA: {ela_score:.2f})")
    if dc_score > 0.45:
        diagnostics.append(f"Double-JPEG quantization comb detected (Score: {dc_score:.2f})")
    if not diagnostics:
        diagnostics.append("Image exhibits authentic, uniform document characteristics.")

    return {
        "tamper_score": round(tamper_score, 4),
        "signals": {
            "ela_score": round(ela_score, 4),
            "copy_move_score": round(cm_score, 4),
            "double_compression_score": round(dc_score, 4),
        },
        "is_tampered": tamper_score >= 0.50,
        "diagnostics": diagnostics,
        "ela_overlay": ela_img,
        "copy_move_overlay": cm_overlay,
        "heatmap_overlay": heatmap_overlay,
        "copy_move_clusters": cm_clusters,
    }
