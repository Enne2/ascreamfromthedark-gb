import cv2
import numpy as np
from pyboy import PyBoy

def main():
    # Load PyBoy with the test gameover ROM
    pyboy = PyBoy('test_gameover.gb', window='null', cgb=False)
    
    # Tick for 120 frames to let the game boot and sprites render
    for _ in range(120):
        pyboy.tick()
        
    # Grab screen buffer and convert it to OpenCV format
    screen_image = pyboy.screen.image
    # screen_image is a PIL Image. Convert to numpy array (RGB)
    img_np = np.array(screen_image)
    # Convert RGB to BGR for OpenCV
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    # Save the screenshot
    cv2.imwrite('gameover_rendering.png', img_bgr)
    print("Screenshot saved to gameover_rendering.png")
    
    # Analyze alignment using OpenCV
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    print(f"Screen size: {w}x{h}")
    
    # The background is white/light (value 255). The text has black/dark pixels.
    # We use BINARY_INV to detect dark objects.
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    
    # Find all contours in the thresholded image
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Find the bounding box of elements in the lower half of the screen (y > 100) where "GAME OVER" is rendered
    gameover_boxes = []
    player_boxes = []
    
    for cnt in contours:
        x, y, rw, rh = cv2.boundingRect(cnt)
        if y > 80:
            gameover_boxes.append((x, y, rw, rh))
        else:
            player_boxes.append((x, y, rw, rh))
            
    # Combine bounding boxes of GAME OVER parts
    if len(gameover_boxes) > 0:
        min_x = min(box[0] for box in gameover_boxes)
        max_x = max(box[0] + box[2] for box in gameover_boxes)
        min_y = min(box[1] for box in gameover_boxes)
        max_y = max(box[1] + box[3] for box in gameover_boxes)
        
        text_width = max_x - min_x
        text_height = max_y - min_y
        center_x = min_x + text_width / 2.0
        
        print("\n--- OpenCV Alignment Verification ---")
        print(f"GAME OVER text bounding box: x={min_x}, y={min_y}, w={text_width}, h={text_height}")
        print(f"GAME OVER text horizontal center: {center_x}")
        print(f"Target screen center: {w / 2.0}")
        
        # Verify alignment within 2 pixels tolerance
        offset = abs(center_x - (w / 2.0))
        print(f"Alignment offset: {offset} pixels")
        if offset <= 2.0:
            print("SUCCESS: The GAME OVER text is absolutely aligned (perfectly centered)!")
        else:
            print(f"WARNING: The GAME OVER text is off-center by {offset} pixels.")
    else:
        print("Error: Could not detect the GAME OVER text in the lower half of the screen.")
        
    pyboy.stop()

if __name__ == '__main__':
    main()
