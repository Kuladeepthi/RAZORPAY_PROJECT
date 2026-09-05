"""
SentinelEvidence — Forensic Signal 2: Clustered Translation Vector Copy-Move Detector

Detects true cloned document regions (stamps, signatures, duplicate boxes) by verifying:
1. 32x32 Normalized Cross-Correlation (NCC >= 0.90) on complex patches.
2. Spatial Translation Consistency: Requires a cluster of at least 4 keypoints sharing
   the exact same displacement vector (dx, dy) within a 20px grid.
"""

from collections import Counter
from typing import Tuple, Union, List, Dict, Any
import numpy as np
import cv2
from PIL import Image


def detect_copy_move(
    image_input: Union[str, np.ndarray, Image.Image],
    min_cluster_size: int = 5,
    distance_threshold: int = 36,
    min_spatial_distance: float = 45.0,
    patch_size: int = 36
) -> Tuple[np.ndarray, float, List[Dict[str, Any]]]:
    if isinstance(image_input, str):
        img_bgr = cv2.imread(image_input)
        if img_bgr is None:
            raise FileNotFoundError(f"Could not load image from {image_input}")
    elif isinstance(image_input, Image.Image):
        img_bgr = cv2.cvtColor(np.array(image_input.convert("RGB")), cv2.COLOR_RGB2BGR)
    elif isinstance(image_input, np.ndarray):
        img_bgr = image_input.copy()
        if len(img_bgr.shape) == 2:
            img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_GRAY2BGR)
    else:
        raise ValueError(f"Unsupported image input type: {type(image_input)}")

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    overlay = img_bgr.copy()
    h, w = gray.shape

    orb = cv2.ORB_create(nfeatures=2500, fastThreshold=12)
    keypoints, descriptors = orb.detectAndCompute(gray, None)

    if descriptors is None or len(keypoints) < 10:
        return overlay, 0.0, []

    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    matches = bf.knnMatch(descriptors, descriptors, k=3)

    half_p = patch_size // 2
    matched_pairs = []
    translation_vectors = []

    for m_list in matches:
        if len(m_list) >= 2:
            m = m_list[1]
            if m.distance < distance_threshold:
                p1 = np.array(keypoints[m.queryIdx].pt, dtype=int)
                p2 = np.array(keypoints[m.trainIdx].pt, dtype=int)
                
                if np.linalg.norm(p1 - p2) >= min_spatial_distance:
                    x1, y1 = p1[0] - half_p, p1[1] - half_p
                    x2, y2 = p2[0] - half_p, p2[1] - half_p
                    
                    if 0 <= x1 < w - patch_size and 0 <= y1 < h - patch_size and 0 <= x2 < w - patch_size and 0 <= y2 < h - patch_size:
                        patch1 = gray[y1 : y1 + patch_size, x1 : x1 + patch_size].astype(np.float32)
                        patch2 = gray[y2 : y2 + patch_size, x2 : x2 + patch_size].astype(np.float32)
                        
                        if np.var(patch1) > 100 and np.var(patch2) > 100:
                            p1_n = (patch1 - np.mean(patch1)) / (np.std(patch1) + 1e-5)
                            p2_n = (patch2 - np.mean(patch2)) / (np.std(patch2) + 1e-5)
                            ncc = float(np.mean(p1_n * p2_n))
                            
                            if ncc >= 0.90:
                                dx = int(round((p2[0] - p1[0]) / 20.0))
                                dy = int(round((p2[1] - p1[1]) / 20.0))
                                translation_vectors.append((dx, dy))
                                matched_pairs.append((p1, p2, ncc, (dx, dy)))

    if not translation_vectors:
        return overlay, 0.0, []

    # Count clusters of identical displacement vectors
    vector_counts = Counter(translation_vectors)
    best_vector, max_cluster = vector_counts.most_common(1)[0]

    detected_clusters = []
    if max_cluster >= min_cluster_size:
        for p1, p2, ncc, shift in matched_pairs:
            if shift == best_vector:
                p1_t = tuple(p1)
                p2_t = tuple(p2)
                cv2.circle(overlay, p1_t, 10, (0, 0, 255), 2)
                cv2.circle(overlay, p2_t, 10, (255, 0, 0), 2)
                cv2.line(overlay, p1_t, p2_t, (0, 255, 255), 1)
                detected_clusters.append({
                    "src_point": p1_t,
                    "dst_point": p2_t,
                    "ncc": round(ncc, 3),
                    "distance": float(np.linalg.norm(p1 - p2))
                })

        score = float(np.clip((max_cluster - 3) / 5.0, 0.0, 1.0))
        return overlay, score, detected_clusters

    return overlay, 0.0, []
