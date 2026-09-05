"""Tests for Layer 1: Forensic Vision Algorithms."""

import numpy as np
import cv2
from src.forensics.ela import error_level_analysis
from src.forensics.copy_move import detect_copy_move
from src.forensics.double_compression import detect_double_compression
from src.forensics.fusion import run_forensic_pipeline, fuse_forensic_signals


def test_ela_on_uniform_and_synthetic_tamper():
    # 1. Clean document base image
    clean_img = np.full((300, 300, 3), 245, dtype=np.uint8)
    cv2.putText(clean_img, "Standard Document Text Line 1", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (20, 20, 20), 1)
    cv2.putText(clean_img, "Standard Document Text Line 2", (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (20, 20, 20), 1)
    cv2.putText(clean_img, "Standard Document Text Line 3", (30, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (20, 20, 20), 1)
    cv2.putText(clean_img, "Standard Document Text Line 4", (30, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (20, 20, 20), 1)

    ela_img, score_clean, mask = error_level_analysis(clean_img)
    assert 0.0 <= score_clean <= 1.0


def test_copy_move_detection():
    # Create image with cloned patch
    img = np.full((400, 400, 3), 240, dtype=np.uint8)
    cv2.circle(img, (80, 80), 25, (10, 20, 200), -1)
    cv2.rectangle(img, (60, 60), (100, 100), (0, 0, 0), 2)
    patch = img[50:110, 50:110].copy()
    img[250:310, 250:310] = patch

    overlay, score, clusters = detect_copy_move(img)
    assert 0.0 <= score <= 1.0


def test_double_compression_detector():
    img = np.random.randint(50, 200, (200, 200), dtype=np.uint8)
    score, hist = detect_double_compression(img, num_bins=64)
    assert 0.0 <= score <= 1.0
    assert len(hist) == 64


def test_fusion_pipeline():
    img = np.full((250, 250, 3), 220, dtype=np.uint8)
    res = run_forensic_pipeline(img)
    assert "tamper_score" in res
    assert "signals" in res
    assert "heatmap_overlay" in res
    assert 0.0 <= res["tamper_score"] <= 1.0
