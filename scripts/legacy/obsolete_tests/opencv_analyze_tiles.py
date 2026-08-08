import cv2
import numpy as np

def main():
    img = cv2.imread('hello_iso_gb.png')
    if img is None:
        print("Error: Could not load hello_iso_gb.png")
        return
        
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    
    # Create a markup copy of the image
    markup = img.copy()
    
    # We want to detect the rendering glitches (black V-shapes or gaps cutting into the floor tiles)
    # The floor tiles are White (255) and Light Gray (153) with Dark Gray (85) lines.
    # The empty background is Black (0).
    # Inside the walkable path, any Black (0) pixel that is surrounded by floor tile colors
    # represents a cutout glitch.
    # Let's use morphological operations to find these black cutouts inside the tiles.
    
    # Threshold to find floor tiles (value > 50, so anything not black)
    _, floor_mask = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
    
    # Invert to find black pixels
    black_mask = cv2.bitwise_not(floor_mask)
    
    # Find contours of the black regions
    contours, _ = cv2.findContours(black_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    glitch_count = 0
    for cnt in contours:
        x, y, rw, rh = cv2.boundingRect(cnt)
        
        # The screen border is black, so we ignore black regions touching the screen boundaries
        if x <= 2 or y <= 2 or (x + rw) >= w - 2 or (y + rh) >= h - 2:
            continue
            
        # Glitches are small black gaps/triangles. Typically small (e.g. area between 4 and 40 pixels)
        area = cv2.contourArea(cnt)
        if 2 <= area <= 50:
            # Check if it's inside the checkerboard area
            # (which is roughly centered on the screen)
            cv2.rectangle(markup, (x, y), (x + rw, y + rh), (0, 0, 255), 1) # Red box
            glitch_count += 1
            
    print(f"Detected {glitch_count} rendering glitches (black cutouts/gaps) inside the floor map.")
    
    # Save the marked-up image to the artifacts directory
    output_path = '/home/enne2/.gemini/antigravity-ide/brain/dd9e728a-93c4-49f8-90b6-3f72fcc47f04/analyzed_tiles.png'
    cv2.imwrite(output_path, markup)
    print(f"Saved analysis markup to: {output_path}")

if __name__ == '__main__':
    main()
