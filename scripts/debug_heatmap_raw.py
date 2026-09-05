import sys
from pathlib import Path
import cv2
import numpy as np

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.forensics.ela import error_level_analysis
from src.forensics.copy_move import detect_copy_move
from src.forensics.fusion import run_forensic_pipeline, generate_tamper_heatmap

def debug_genuine_invoice():
    print("=" * 70)
    print("DEBUGGING GENUINE INVOICE HEATMAP & ALPHA VALUES")
    print("=" * 70)
    
    img_path = "data/templates/gst_invoice_apex_01.png"
    img_bgr = cv2.imread(img_path)
    print(f"Loaded image from '{img_path}': shape={img_bgr.shape}, dtype={img_bgr.dtype}")
    
    # 1. Check ELA
    ela_img, ela_score, ela_mask = error_level_analysis(img_path)
    print(f"ELA score: {ela_score}, ela_mask shape={ela_mask.shape}, min={ela_mask.min()}, max={ela_mask.max()}, mean={ela_mask.mean()}")
    
    # 2. Check Copy-Move
    cm_overlay, cm_score, cm_clusters = detect_copy_move(img_bgr)
    print(f"Copy-Move score: {cm_score}, clusters={len(cm_clusters)}")
    
    # 3. Check generate_tamper_heatmap internals
    h, w = img_bgr.shape[:2]
    density_map = np.zeros((h, w), dtype=np.float32)
    if ela_mask is not None and ela_mask.size > 0:
        ela_resized = cv2.resize(ela_mask, (w, h))
        ela_norm = ela_resized.astype(np.float32) / 255.0
        ela_filtered = np.where(ela_norm > 0.15, ela_norm, 0.0)
        density_map += ela_filtered * 0.85
        print(f"Density map from ELA: min={density_map.min()}, max={density_map.max()}, mean={density_map.mean()}")

    blurred = cv2.GaussianBlur(density_map, (35, 35), 0)
    hotspot_intensity = np.clip((blurred - 0.06) / 0.94, 0.0, 1.0)
    print(f"Hotspot intensity: min={hotspot_intensity.min()}, max={hotspot_intensity.max()}, mean={hotspot_intensity.mean()}")
    
    sample_coords = [(100, 100), (200, 200), (300, 300), (400, 400), (500, 500)]
    for pt in sample_coords:
        print(f"  Coord {pt}: intensity={hotspot_intensity[pt[0], pt[1]]}, original_bgr={img_bgr[pt[0], pt[1]]}")

    # 4. Check full pipeline return
    res = run_forensic_pipeline(img_bgr)
    hm = res["heatmap_overlay"]
    print(f"Heatmap overlay shape: {hm.shape}, dtype={hm.dtype}")
    for pt in sample_coords:
        print(f"  Coord {pt}: original={img_bgr[pt[0], pt[1]]} -> heatmap={hm[pt[0], pt[1]]} (diff={abs(int(img_bgr[pt[0], pt[1]][0]) - int(hm[pt[0], pt[1]][0]))})")
        
    diff = np.abs(img_bgr.astype(int) - hm.astype(int))
    print(f"Total non-zero pixel diff count: {np.count_nonzero(diff)} / {img_bgr.size}")

if __name__ == "__main__":
    debug_genuine_invoice()
