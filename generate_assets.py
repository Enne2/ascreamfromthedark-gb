import os
from PIL import Image, ImageDraw

# Standard Game Boy palette
# 0: White, 1: Light Gray, 2: Dark Gray, 3: Black
PALETTE = [
    255, 255, 255, # 0
    170, 170, 170, # 1
    85, 85, 85,    # 2
    0, 0, 0        # 3
] + [0] * (256 * 3 - 12)

def draw_autotile(draw, y_offset, is_alt, mask):
    # Determine the neighbor fill color
    # Tile 1 (Normal, is_alt=False) neighbors should match Tile 2 (Alt) body color: 1 (Light Gray)
    # Tile 2 (Alt, is_alt=True) neighbors should match Tile 1 (Normal) body color: 0 (White)
    neighbor_color = 0 if is_alt else 1
    
    # 4 corners
    # Bit 0 (1): Top-Left
    # Bit 1 (2): Top-Right
    # Bit 2 (4): Bottom-Left
    # Bit 3 (8): Bottom-Right
    
    tl_color = neighbor_color if (mask & 1) else 3
    tr_color = neighbor_color if (mask & 2) else 3
    dl_color = neighbor_color if (mask & 4) else 3
    dr_color = neighbor_color if (mask & 8) else 3
    
    # Draw corners
    draw.polygon([(0, y_offset), (15, y_offset), (0, y_offset + 7)], fill=tl_color)
    draw.polygon([(16, y_offset), (31, y_offset), (31, y_offset + 7)], fill=tr_color)
    draw.polygon([(0, y_offset + 8), (0, y_offset + 15), (15, y_offset + 15)], fill=dl_color)
    draw.polygon([(31, y_offset + 8), (31, y_offset + 15), (16, y_offset + 15)], fill=dr_color)
    
    # Draw the main diamond shape on top
    points = [(15, y_offset), (31, y_offset + 7), (16, y_offset + 15), (0, y_offset + 8)]
    inner = [(15, y_offset + 4), (27, y_offset + 7), (16, y_offset + 11), (4, y_offset + 8)]
    
    if not is_alt:
        # Tile 1: Normal floor (body is White, inner is Light Gray)
        draw.polygon(points, fill=0, outline=2)
        draw.polygon(inner, fill=1, outline=2)
    else:
        # Tile 2: Alt floor (body is Light Gray, inner is White)
        draw.polygon(points, fill=1, outline=2)
        draw.polygon(inner, fill=0, outline=2)

def generate_tiles():
    # 32 variants total:
    # 0..15: Tile 1 (Normal Floor) with masks 0..15
    # 16..31: Tile 2 (Alt Floor) with masks 0..15
    # Height is 8 pixels (black spacer) + 32 variants * 16 pixels = 520 pixels
    img = Image.new("P", (32, 520), 3)
    img.putpalette(PALETTE)
    draw = ImageDraw.Draw(img)
    
    # Draw Tile 1 variants (start at y=8)
    for mask in range(16):
        draw_autotile(draw, 8 + mask * 16, False, mask)
        
    # Draw Tile 2 variants (start at y=8 + 256 = 264)
    for mask in range(16):
        draw_autotile(draw, 264 + mask * 16, True, mask)
        
    img.save("tiles.png")

# Grids for player frames
# 0 = White, 1 = Light Gray, 2 = Dark Gray, 3 = Black

# Down-Right Stand (Frame 0)
GRID_DR_STAND = [
    "0000000000000000",
    "0000003333000000",
    "0000031111300000",
    "0000311111130000",
    "0000311313130000", # Eyes facing right/down
    "0000031111300000",
    "0000003333000000",
    "0000032222300000",
    "0000312222130000",
    "0000312222130000",
    "0000032222300000",
    "0000003333000000",
    "0000033003300000",
    "0000033003300000",
    "0000333003330000",
    "0000000000000000"
]

# Down-Right Walk (Frame 1)
GRID_DR_WALK = [
    "0000000000000000",
    "0000003333000000",
    "0000031111300000",
    "0000311111130000",
    "0000311313130000",
    "0000031111300000",
    "0000003333000000",
    "0000032222300000",
    "0000312222130000",
    "0000312222130000",
    "0000032222300000",
    "0000003333000000",
    "0000033000030000", # Left leg forward, right leg back
    "0000330000033000",
    "0003330000033300",
    "0000000000000000"
]

# Up-Right Stand (Frame 4 in final list)
GRID_UR_STAND = [
    "0000000000000000",
    "0000003333000000",
    "0000031111300000",
    "0000311111130000",
    "0000311111130000", # Back of head (no eyes)
    "0000031111300000",
    "0000003333000000",
    "0000032222300000",
    "0000312222130000",
    "0000312222130000",
    "0000032222300000",
    "0000003333000000",
    "0000033003300000",
    "0000033003300000",
    "0000333003330000",
    "0000000000000000"
]

# Up-Right Walk (Frame 5 in final list)
GRID_UR_WALK = [
    "0000000000000000",
    "0000003333000000",
    "0000031111300000",
    "0000311111130000",
    "0000311111130000",
    "0000031111300000",
    "0000003333000000",
    "0000032222300000",
    "0000312222130000",
    "0000312222130000",
    "0000032222300000",
    "0000003333000000",
    "0000033000030000",
    "0000330000033000",
    "0003330000033300",
    "0000000000000000"
]

def draw_frame(draw, grid, x_off):
    for y in range(16):
        for x in range(16):
            val = int(grid[y][x])
            draw.point((x_off + x, y), fill=val)

def generate_player():
    # 8 frames in total (128x16 pixels)
    player_img = Image.new("P", (128, 16), 0)
    player_img.putpalette(PALETTE)
    
    dr_stand = Image.new("P", (16, 16), 0)
    dr_stand.putpalette(PALETTE)
    draw_frame(ImageDraw.Draw(dr_stand), GRID_DR_STAND, 0)
    
    dr_walk = Image.new("P", (16, 16), 0)
    dr_walk.putpalette(PALETTE)
    draw_frame(ImageDraw.Draw(dr_walk), GRID_DR_WALK, 0)
    
    ur_stand = Image.new("P", (16, 16), 0)
    ur_stand.putpalette(PALETTE)
    draw_frame(ImageDraw.Draw(ur_stand), GRID_UR_STAND, 0)
    
    ur_walk = Image.new("P", (16, 16), 0)
    ur_walk.putpalette(PALETTE)
    draw_frame(ImageDraw.Draw(ur_walk), GRID_UR_WALK, 0)
    
    dl_stand = dr_stand.transpose(Image.FLIP_LEFT_RIGHT)
    dl_walk = dr_walk.transpose(Image.FLIP_LEFT_RIGHT)
    ul_stand = ur_stand.transpose(Image.FLIP_LEFT_RIGHT)
    ul_walk = ur_walk.transpose(Image.FLIP_LEFT_RIGHT)
    
    player_img.paste(dr_stand, (0 * 16, 0))
    player_img.paste(dr_walk, (1 * 16, 0))
    player_img.paste(dl_stand, (2 * 16, 0))
    player_img.paste(dl_walk, (3 * 16, 0))
    player_img.paste(ul_stand, (4 * 16, 0))
    player_img.paste(ul_walk, (5 * 16, 0))
    player_img.paste(ur_stand, (6 * 16, 0))
    player_img.paste(ur_walk, (7 * 16, 0))
    
    player_img.save("player.png")

if __name__ == "__main__":
    generate_tiles()
    generate_player()
    print("PNG assets generated (32x520 tiles, 8-frame player animation set created).")
