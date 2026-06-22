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

def draw_autotile(draw, y_offset, is_alt, mask, is_dark=False):
    # Determine the neighbor fill color
    # Tile 1 (Normal, is_alt=False) neighbors should match Tile 2 (Alt) body color: 1 (Light Gray)
    # Tile 2 (Alt, is_alt=True) neighbors should match Tile 1 (Normal) body color: 0 (White)
    if not is_dark:
        neighbor_color = 0 if is_alt else 1
        
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
    else:
        # Darker version: Shift colors down
        # White (0) -> Light Gray (1)
        # Light Gray (1) -> Dark Gray (2)
        # Dark Gray (2) -> Black (3)
        # Black (3) -> Black (3)
        neighbor_color = 1 if is_alt else 2
        
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
            # Tile 1 Dark: body is Light Gray (1), inner is Dark Gray (2), outline is Black (3)
            draw.polygon(points, fill=1, outline=3)
            draw.polygon(inner, fill=2, outline=3)
        else:
            # Tile 2 Dark: body is Dark Gray (2), inner is Light Gray (1), outline is Black (3)
            draw.polygon(points, fill=2, outline=3)
            draw.polygon(inner, fill=1, outline=3)

def generate_tiles():
    # 64 variants total:
    # 0..15: Tile 1 (Normal Floor) with masks 0..15
    # 16..31: Tile 2 (Alt Floor) with masks 0..15
    # 32..47: Tile 1 Dark (Normal Floor Dark) with masks 0..15
    # 48..63: Tile 2 Dark (Alt Floor Dark) with masks 0..15
    # Height is 8 pixels (black spacer) + 64 variants * 16 pixels = 1032 pixels
    img = Image.new("P", (32, 1032), 3)
    img.putpalette(PALETTE)
    draw = ImageDraw.Draw(img)
    
    # Draw Tile 1 variants (start at y=8)
    for mask in range(16):
        draw_autotile(draw, 8 + mask * 16, False, mask, False)
        
    # Draw Tile 2 variants (start at y=264)
    for mask in range(16):
        draw_autotile(draw, 264 + mask * 16, True, mask, False)

    # Draw Tile 1 Dark variants (start at y=520)
    for mask in range(16):
        draw_autotile(draw, 520 + mask * 16, False, mask, True)

    # Draw Tile 2 Dark variants (start at y=776)
    for mask in range(16):
        draw_autotile(draw, 776 + mask * 16, True, mask, True)
        
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
