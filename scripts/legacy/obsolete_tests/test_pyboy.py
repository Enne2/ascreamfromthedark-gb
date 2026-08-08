from pyboy import PyBoy

def main():
    pyboy = PyBoy('hello_iso.gb', window='null', cgb=False)
    # Tick a few frames to let the map render
    for _ in range(60 * 2):
        pyboy.tick()
        
    pyboy.screen.image.save('hello_iso_gb.png')
    pyboy.stop()
    print("Screenshot saved to hello_iso_gb.png")

if __name__ == "__main__":
    main()
