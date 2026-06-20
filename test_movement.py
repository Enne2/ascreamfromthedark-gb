from pyboy import PyBoy
from pyboy.utils import WindowEvent

def main():
    pyboy = PyBoy('hello_iso.gb', window='null', cgb=False)
    # Let the game boot and generate the maze
    for _ in range(60 * 2):
        pyboy.tick()
        
    # Read player position from RAM
    # player_lx at 0xC4E8, player_ly at 0xC4E9
    lx = pyboy.memory[0xC4E8]
    ly = pyboy.memory[0xC4E9]
    print(f"Initial player coordinates in RAM: lx={lx}, ly={ly}")
    
    # Read maze array from RAM (7x7 starting at 0xC0B1)
    maze = []
    for y in range(7):
        row = []
        for x in range(7):
            val = pyboy.memory[0xC0B1 + y * 7 + x]
            row.append(val)
        maze.append(row)
        
    print("\nMaze layout in RAM (0=wall, 1=path):")
    for y, row in enumerate(maze):
        row_str = f"{y:02d}: "
        for x, val in enumerate(row):
            if x == lx and y == ly:
                row_str += "P" # Player
            else:
                row_str += str(val)
        print(row_str)
        
    # Check neighbors of player
    print(f"\nPlayer neighbors: Up={maze[ly-1][lx]}, Down={maze[ly+1][lx]}, Left={maze[ly][lx-1]}, Right={maze[ly][lx+1]}")
    
    # Try pressing Down (Down-Left)
    print("\nSimulating pressing DOWN...")
    pyboy.send_input(WindowEvent.PRESS_ARROW_DOWN)
    pyboy.tick()
    pyboy.send_input(WindowEvent.RELEASE_ARROW_DOWN)
    for _ in range(30):
        pyboy.tick()
    print(f"Player coordinates after DOWN: lx={pyboy.memory[0xC4E8]}, ly={pyboy.memory[0xC4E9]}")
    
    # Try pressing Right (Down-Right)
    print("\nSimulating pressing RIGHT...")
    pyboy.send_input(WindowEvent.PRESS_ARROW_RIGHT)
    pyboy.tick()
    pyboy.send_input(WindowEvent.RELEASE_ARROW_RIGHT)
    for _ in range(30):
        pyboy.tick()
    print(f"Player coordinates after RIGHT: lx={pyboy.memory[0xC4E8]}, ly={pyboy.memory[0xC4E9]}")
    
    pyboy.stop()

if __name__ == "__main__":
    main()
