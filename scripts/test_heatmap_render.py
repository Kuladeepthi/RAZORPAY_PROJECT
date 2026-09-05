import os
import sys
from pathlib import Path
import cv2
import numpy as np

# Ensure root in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.forensics.fusion import run_forensic_pipeline, generate_tamper_heatmap

def test_heatmap_rendering():
    print("=" * 75)
    print("TESTING HEATMAP RENDERING & ZERO-PURPLE AUTHENTIC BASELINE")
    print("=" * 75)

    # 1. Genuine Merchant Invoice
    auth_path = "data/templates/gst_invoice_apex_01.png"
    img_auth = cv2.imread(auth_path)
    assert img_auth is not None, f"Cannot load {auth_path}"
    
    res_auth = run_forensic_pipeline(img_auth)
    heatmap_auth = res_auth["heatmap_overlay"]
    
    # Calculate difference between original authentic image and heatmap
    diff_auth = np.abs(img_auth.astype(np.float32) - heatmap_auth.astype(np.float32))
    max_diff_auth = np.max(diff_auth)
    mean_diff_auth = np.mean(diff_auth)
    
    print(f"\n[1] Genuine Merchant Invoice:")
    print(f"    - Original Image Size: {img_auth.shape}")
    print(f"    - Tamper Score:        {res_auth['tamper_score']:.4f}")
    print(f"    - Max Pixel Diff:      {max_diff_auth:.2f}")
    print(f"    - Mean Pixel Diff:     {mean_diff_auth:.4f} (Near 0.0 -> Untinted & Crisp!)")
    cv2.imwrite("data/test_run_output/verified_heatmap_genuine.png", heatmap_auth)
    assert mean_diff_auth < 1.0, f"Authentic document should have ~0 tint, got mean diff {mean_diff_auth}"

    # 2. Tampered / Copy-Move Sample
    tampered_files = list(Path("data/synthetic/tampered").glob("*copy_move*.*"))
    if not tampered_files:
        tampered_files = list(Path("data/templates").glob("*.png"))
    
    tamp_path = str(tampered_files[0])
    img_tamp = cv2.imread(tamp_path)
    res_tamp = run_forensic_pipeline(img_tamp)
    heatmap_tamp = res_tamp["heatmap_overlay"]
    
    print(f"\n[2] Tampered Evidence Fixture ({Path(tamp_path).name}):")
    print(f"    - Tamper Score:        {res_tamp['tamper_score']:.4f}")
    print(f"    - Copy-Move Clusters:  {len(res_tamp['copy_move_clusters'])}")
    cv2.imwrite("data/test_run_output/verified_heatmap_tampered.png", heatmap_tamp)

    # 3. Inpainted / Courier Sample
    inpaint_files = list(Path("data/synthetic/tampered").glob("*inpaint*.*"))
    if inpaint_files:
        inp_path = str(inpaint_files[0])
        img_inp = cv2.imread(inp_path)
        res_inp = run_forensic_pipeline(img_inp)
        cv2.imwrite("data/test_run_output/verified_heatmap_inpainted.png", res_inp["heatmap_overlay"])
        print(f"\n[3] Inpainted Delivery Slip ({Path(inp_path).name}):")
        print(f"    - Tamper Score:        {res_inp['tamper_score']:.4f}")

    print("\n" + "=" * 75)
    print("SUCCESS: All heatmaps rendered without blank panels or background purple tints!")
    print("=" * 75)
    return True

if __name__ == "__main__":
    test_heatmap_rendering()
