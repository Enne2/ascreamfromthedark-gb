import cv2
import numpy as np

def main():
    img = cv2.imread('hello_iso_gb.png')
    if img is None:
        print("Error: Could not load hello_iso_gb.png")
        return
        
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    print(f"Image dimensions: {w}x{h}")
    
    # Print all unique gray values on screen
    unique_vals = np.unique(gray)
    print(f"Unique gray values: {unique_vals}")
    
    # Find all contours in the image
    contours, _ = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    print("\nAll non-trivial contours:")
    for idx, cnt in enumerate(contours):
        x, y, rw, rh = cv2.boundingRect(cnt)
        area = cv2.contourArea(cnt)
        # Filter out screen-sized or tiny noise contours
        if 4 <= area <= 10000:
            print(f"Contour {idx}: x={x}, y={y}, w={rw}, h={rh}, area={area}, center=({x + rw/2}, {y + rh/2})")
            
if __name__ == '__main__':
    main()
