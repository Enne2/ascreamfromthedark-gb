from pyboy import PyBoy
from pyboy.utils import WindowEvent

def get_symbol_address(symbol_name):
    try:
        with open('hello_iso.noi', 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 3 and parts[0] == 'DEF' and parts[1] == symbol_name:
                    return int(parts[2], 16)
    except FileNotFoundError:
        pass
    raise ValueError(f"Symbol {symbol_name} not found in hello_iso.noi")

def main():
    pyboy = PyBoy('hello_iso.gb', window='null', cgb=False)
    # Let the game boot and generate the maze
    for _ in range(60 * 2):
        pyboy.tick()
        
    # Dynamically look up addresses
    player_lx_addr = get_symbol_address('_player_lx')
    player_ly_addr = get_symbol_address('_player_ly')
    maze_addr = get_symbol_address('_maze')
    
    # Read player position from RAM
    lx = pyboy.memory[player_lx_addr]
    ly = pyboy.memory[player_ly_addr]
    print(f"Initial player coordinates in RAM: lx={lx}, ly={ly}")
    
    # Read maze array from RAM (15x15 starting at maze_addr)
    map_size = 15
    maze = []
    for y in range(map_size):
        row = []
        for x in range(map_size):
            val = pyboy.memory[maze_addr + y * map_size + x]
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
    print(f"Player coordinates after DOWN: lx={pyboy.memory[player_lx_addr]}, ly={pyboy.memory[player_ly_addr]}")
    
    # Try pressing Right (Down-Right)
    print("\nSimulating pressing RIGHT...")
    pyboy.send_input(WindowEvent.PRESS_ARROW_RIGHT)
    pyboy.tick()
    pyboy.send_input(WindowEvent.RELEASE_ARROW_RIGHT)
    for _ in range(30):
        pyboy.tick()
    print(f"Player coordinates after RIGHT: lx={pyboy.memory[player_lx_addr]}, ly={pyboy.memory[player_ly_addr]}")
    
    pyboy.stop()

if __name__ == "__main__":
    main()
