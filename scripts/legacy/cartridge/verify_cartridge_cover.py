#!/usr/bin/env python3
import sys
import os
import cv2
import numpy as np

def verify_cartridge_cover(image_path="assets/cartridge_cover.png"):
    print("=" * 60)
    print(f"   OPENCV VERIFICATION SUITE: {image_path}")
    print("=" * 60)
    
    if not os.path.exists(image_path):
        print(f"[FAIL] Image file not found: {image_path}")
        return False

    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"[FAIL] Could not load image with OpenCV: {image_path}")
        return False
        
    height, width, channels = img.shape
    print(f"Loaded image: {width} x {height} px with {channels} channels.")
    
    all_passed = True
    
    # -------------------------------------------------------------
    # TEST 1: Physical Aspect Ratio & Dimensions (42mm x 37mm spec)
    # -------------------------------------------------------------
    expected_w = 1008
    expected_h = 888
    target_aspect = 42.0 / 37.0  # ~1.1351
    actual_aspect = width / float(height)
    aspect_diff = abs(actual_aspect - target_aspect)
    
    print("\n--- TEST 1: Dimensions & Aspect Ratio ---")
    if (width, height) == (expected_w, expected_h) and aspect_diff < 0.01:
        print(f"  [PASS] Resolution: {width}x{height} px | Aspect Ratio: {actual_aspect:.4f} (Target: {target_aspect:.4f})")
    else:
        print(f"  [FAIL] Incorrect size or aspect ratio: {width}x{height} px, ratio {actual_aspect:.4f}")
        all_passed = False

    # -------------------------------------------------------------
    # TEST 2: Notch Cutout & Alpha Transparency Verification
    # -------------------------------------------------------------
    print("\n--- TEST 2: Top-Left DMG Notch Cutout ---")
    if channels == 4:
        alpha = img[:, :, 3]
        notch_roi = alpha[0:60, 0:60]
        notch_alpha_mean = np.mean(notch_roi)
        
        center_roi = alpha[300:600, 300:600]
        center_alpha_mean = np.mean(center_roi)
        
        if notch_alpha_mean == 0 and center_alpha_mean == 255:
            print(f"  [PASS] Notch ROI alpha: {notch_alpha_mean:.1f} (transparent) | Body ROI alpha: {center_alpha_mean:.1f} (opaque)")
        else:
            print(f"  [FAIL] Alpha mask error. Notch: {notch_alpha_mean:.1f}, Center: {center_alpha_mean:.1f}")
            all_passed = False
    else:
        print("  [FAIL] Image missing alpha channel (expected 4 channels).")
        all_passed = False

    # -------------------------------------------------------------
    # TEST 3: Header Banner Metallic Background & Deep Blue Text ROI
    # -------------------------------------------------------------
    print("\n--- TEST 3: Header Banner & Nintendo GAME BOY Text ---")
    bgr = img[:, :, :3]
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    
    # Silver background region check y in [35, 150], x in [200, 800]
    header_bg_roi = bgr[50:140, 200:800]
    mean_b, mean_g, mean_r = np.mean(header_bg_roi, axis=(0,1))
    
    # Check metallic silver tone (balanced R, G, B > 180)
    silver_valid = (mean_r > 180 and mean_g > 180 and mean_b > 180) and (abs(mean_r - mean_b) < 20)
    
    # Deep blue text threshold in HSV
    lower_blue = np.array([100, 80, 50])
    upper_blue = np.array([135, 255, 220])
    header_hsv_roi = hsv[40:150, 150:900]
    blue_mask = cv2.inRange(header_hsv_roi, lower_blue, upper_blue)
    blue_pixel_count = np.count_nonzero(blue_mask)
    
    if silver_valid and blue_pixel_count > 500:
        print(f"  [PASS] Metallic Silver Background (R:{mean_r:.1f}, G:{mean_g:.1f}, B:{mean_b:.1f})")
        print(f"  [PASS] Blue Header Text Detected: {blue_pixel_count} px in HSV range [100..135]")
    else:
        print(f"  [FAIL] Header color check failed. Silver valid: {silver_valid}, Blue px: {blue_pixel_count}")
        all_passed = False

    # -------------------------------------------------------------
    # TEST 4: Central Artwork Frame Bounding & Contrast
    # -------------------------------------------------------------
    print("\n--- TEST 4: Central Artwork Placement & Contrast ---")
    art_roi = bgr[190:810, 70:930]
    art_gray = cv2.cvtColor(art_roi, cv2.COLOR_BGR2GRAY)
    contrast_std = np.std(art_gray)
    laplacian_var = cv2.Laplacian(art_gray, cv2.CV_64F).var()
    
    # Detect frame edges
    edges = cv2.Canny(art_gray, 50, 150)
    edge_count = np.count_nonzero(edges)
    
    if contrast_std > 40 and laplacian_var > 100 and edge_count > 1000:
        print(f"  [PASS] Artwork ROI Contrast StdDev: {contrast_std:.2f} | Laplacian Var: {laplacian_var:.1f}")
        print(f"  [PASS] Artwork Edge Feature Density: {edge_count} edge px")
    else:
        print(f"  [FAIL] Artwork ROI low contrast or missing content. StdDev: {contrast_std:.2f}")
        all_passed = False

    # -------------------------------------------------------------
    # TEST 5: Bottom Instruction Text Banner ("THIS SIDE OUT")
    # -------------------------------------------------------------
    print("\n--- TEST 5: Bottom Banner Text Detection ---")
    bottom_roi = art_gray = cv2.cvtColor(bgr[830:880, 300:700], cv2.COLOR_BGR2GRAY)
    _, bottom_thresh = cv2.threshold(bottom_roi, 100, 255, cv2.THRESH_BINARY_INV)
    text_pixel_count = np.count_nonzero(bottom_thresh)
    
    if text_pixel_count > 300:
        print(f"  [PASS] Bottom 'THIS SIDE OUT' banner text pixels detected: {text_pixel_count} px")
    else:
        print(f"  [FAIL] Bottom text banner undetected or low contrast ({text_pixel_count} px)")
        all_passed = False

    print("=" * 60)
    if all_passed:
        print("   ALL OPENCV VERIFICATION CHECKS PASSED SUCCESSFULLY! [100%]")
        print("=" * 60)
        return True
    else:
        print("   VERIFICATION FAILED: One or more checks failed.")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = verify_cartridge_cover()
    sys.exit(0 if success else 1)
