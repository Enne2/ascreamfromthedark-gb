from pyboy import PyBoy
import sys

def take_screenshot():
    # Initialize PyBoy in headless mode to not block or require X11
    pyboy = PyBoy('hello_iso.gb', window_type="headless")
    
    # Run for 300 frames to let the PyBoy boot screen finish and the title screen render fully
    for _ in range(300):
        pyboy.tick()
        
    # Take screenshot
    pyboy.screen.image.save('screenshot.png')
    print("Screenshot saved to screenshot.png")
    pyboy.stop()

if __name__ == "__main__":
    take_screenshot()
