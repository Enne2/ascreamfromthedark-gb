import os
from PIL import Image, ImageDraw

# Standard Game Boy palette
# 0: White, 1: Light Gray, 2: Dark Gray, 3: Black
PALETTE = [
    224, 248, 207, # 0
    134, 192, 108, # 1
    48, 104, 80,   # 2
    7, 24, 33      # 3
] + [0] * (256 * 3 - 12)

def draw_corner(draw, corner_type, state, is_alt):
    if state == 0:
        fill_color = 3
        neigh_inner = None
    elif state == 1:
        fill_color = 0 if is_alt else 1
        neigh_inner = 1 if is_alt else 0
        neigh_outline = 2
    else:
        fill_color = 1 if is_alt else 2
        neigh_inner = 2 if is_alt else 1
        neigh_outline = 3
        
    if corner_type == 'tl':
        draw.polygon([(0, 0), (15, 0), (0, 7)], fill=fill_color)
        if state != 0:
            draw.polygon([(-1, -4), (11, -1), (0, 3), (-12, 0)], fill=neigh_inner, outline=neigh_outline)
    elif corner_type == 'tr':
        draw.polygon([(16, 0), (31, 0), (31, 7)], fill=fill_color)
        if state != 0:
            draw.polygon([(31, -4), (43, -1), (32, 3), (20, 0)], fill=neigh_inner, outline=neigh_outline)
    elif corner_type == 'bl':
        draw.polygon([(0, 8), (0, 15), (15, 15)], fill=fill_color)
        if state != 0:
            draw.polygon([(-1, 12), (11, 15), (0, 19), (-12, 16)], fill=neigh_inner, outline=neigh_outline)
    elif corner_type == 'br':
        draw.polygon([(31, 8), (31, 15), (16, 15)], fill=fill_color)
        if state != 0:
            draw.polygon([(31, 12), (43, 15), (32, 19), (20, 16)], fill=neigh_inner, outline=neigh_outline)

def draw_autotile(img, y_offset, is_alt, mask, is_dark=False):
    temp_img = Image.new("P", (32, 16), 3)
    temp_img.putpalette(PALETTE)
    draw = ImageDraw.Draw(temp_img)
    
    tl_state = mask % 3
    tr_state = mask // 3
    body_color = 2 if is_dark else (1 if is_alt else 0)
    outer = [(15, 0), (31, 7), (16, 15), (0, 8)]
    draw.polygon(outer, fill=body_color)
    draw_corner(draw, 'tl', tl_state, is_alt)
    draw_corner(draw, 'tr', tr_state, is_alt)
    draw_corner(draw, 'bl', 0, is_alt)
    draw_corner(draw, 'br', 0, is_alt)
    inner_color = 3 if is_dark else (0 if is_alt else 1)
    if is_dark:
        inner_color = 1 if is_alt else 2
    outline_color = 3 if is_dark else 2
    inner = [(15, 4), (27, 7), (16, 11), (4, 8)]
    draw.polygon(inner, fill=inner_color, outline=outline_color)
    
    img.paste(temp_img, (0, y_offset))

def generate_tiles():
    img = Image.new("P", (32, 5768), 3)
    img.putpalette(PALETTE)
    
    for mask in range(9): draw_autotile(img, 8 + mask * 16, False, mask, False)
    for mask in range(9): draw_autotile(img, 152 + mask * 16, True, mask, False)
    for mask in range(9): draw_autotile(img, 296 + mask * 16, False, mask, True)
    for mask in range(9): draw_autotile(img, 440 + mask * 16, True, mask, True)

    stairs_pattern = [
        "TTTTTTTTTTTTTTT33TTTTTTTTTTTTTTT",
        "TTTTTTTTTTTTT331133TTTTTTTTTTTTT",
        "TTTTTTTTTTT3311111133TTTTTTTTTTT",
        "TTTTTTTTTTTTT331133TTTTTTTTTTTTT",
        "TTTTTTTTTTTTTTT33TTTTTTTTTTTTTTT",
        "TTTTTTTTTTTTT330033TTTTTTTTTTTTT",
        "TTTTTTTTTTT3300000033TTTTTTTTTTT",
        "TTTTTTTTTTTTT330033TTTTTTTTTTTTT",
        "TTTTTTTTTTTTTTT33TTTTTTTTTTTTTTT",
        "TTTTTTTTTTTTT331133TTTTTTTTTTTTT",
        "TTTTTTTTTTT3311111133TTTTTTTTTTT",
        "TTTTTTTTTTTTT331133TTTTTTTTTTTTT",
        "TTTTTTTTTTTTTTT33TTTTTTTTTTTTTTT",
        "TTTTTTTTTTTTT330033TTTTTTTTTTTTT",
        "TTTTTTTTTTT3300000033TTTTTTTTTTT",
        "TTTTTTTTTTTTT330033TTTTTTTTTTTTT",
    ]
    dark_stairs_pattern = [
        "TTTTTTTTTTTTTTT33TTTTTTTTTTTTTTT",
        "TTTTTTTTTTTTT332233TTTTTTTTTTTTT",
        "TTTTTTTTTTT3322222233TTTTTTTTTTT",
        "TTTTTTTTTTTTT332233TTTTTTTTTTTTT",
        "TTTTTTTTTTTTTTT33TTTTTTTTTTTTTTT",
        "TTTTTTTTTTTTT331133TTTTTTTTTTTTT",
        "TTTTTTTTTTT3311111133TTTTTTTTTTT",
        "TTTTTTTTTTTTT331133TTTTTTTTTTTTT",
        "TTTTTTTTTTTTTTT33TTTTTTTTTTTTTTT",
        "TTTTTTTTTTTTT332233TTTTTTTTTTTTT",
        "TTTTTTTTTTT3322222233TTTTTTTTTTT",
        "TTTTTTTTTTTTT332233TTTTTTTTTTTTT",
        "TTTTTTTTTTTTTTT33TTTTTTTTTTTTTTT",
        "TTTTTTTTTTTTT331133TTTTTTTTTTTTT",
        "TTTTTTTTTTT3311111133TTTTTTTTTTT",
        "TTTTTTTTTTTTT331133TTTTTTTTTTTTT",
    ]

    for v_set, base_offset, pattern in [
        (0, 584, stairs_pattern), 
        (1, 1880, stairs_pattern),
        (2, 3176, dark_stairs_pattern),
        (3, 4472, dark_stairs_pattern)
    ]:
        is_alt_vic = (v_set == 1 or v_set == 3)
        is_dark_vic = (v_set == 2 or v_set == 3)
        for mask in range(81):
            y_offset = base_offset + mask * 16
            
            tl_state = mask % 3
            tr_state = (mask // 3) % 3
            bl_state = (mask // 9) % 3
            br_state = (mask // 27) % 3
            
            temp_img = Image.new("P", (32, 16), 3)
            temp_img.putpalette(PALETTE)
            draw = ImageDraw.Draw(temp_img)
            
            body_color = 2 if is_dark_vic else (1 if is_alt_vic else 0)
            outer = [(15, 0), (31, 7), (16, 15), (0, 8)]
            draw.polygon(outer, fill=body_color)
            
            draw_corner(draw, 'tl', tl_state, is_alt_vic)
            draw_corner(draw, 'tr', tr_state, is_alt_vic)
            draw_corner(draw, 'bl', bl_state, is_alt_vic)
            draw_corner(draw, 'br', br_state, is_alt_vic)
            
            for py in range(16):
                for px in range(32):
                    char = pattern[py][px]
                    if char != 'T':
                        temp_img.putpixel((px, py), int(char))
            
            img.paste(temp_img, (0, y_offset))

    img.save("tiles.png")

def generate_stamina():
    # 13 variants of 8x16 tiles = 104x16 pixels
    img = Image.new("P", (104, 16), 0) # Fill with 0 (transparent)
    img.putpalette(PALETTE)
    
    def draw_sprite_bar_tile(x_off, filled_px, cap=None):
        for y in range(8):
            for x in range(8):
                color = 3 # black inside
                if y == 0 or y == 7:
                    color = 3 # black border
                elif y == 1 or y == 6:
                    color = 2 # dark gray inner border
                else:
                    if x < filled_px:
                        color = 1 # light gray (filled)
                    else:
                        color = 3 # black (empty)
                        
                if cap == 'L' and x == 0:
                    color = 2 # left border
                elif cap == 'R' and x == 7:
                    color = 2 # right border
                    
                img.putpixel((x_off + x, y), color)
                
    # Also fill bottom 8 rows with transparent color 0
    for y in range(8, 16):
        for x in range(104):
            img.putpixel((x, y), 0)
            
    for i in range(9):
        draw_sprite_bar_tile(i * 8, i)
        
    draw_sprite_bar_tile(9 * 8, 0, 'L')
    draw_sprite_bar_tile(10 * 8, 0, 'R')
    draw_sprite_bar_tile(11 * 8, 8, 'L')
    draw_sprite_bar_tile(12 * 8, 8, 'R')
    
    img.save("stamina.png")

# Grids for player frames
# 0 = White, 1 = Light Gray, 2 = Dark Gray, 3 = Black

# Down-Right Stand (Frame 0)
GRID_DR_STAND = [
    "0000333333330000",
    "0003222222223000",
    "0032233333322300",
    "0032321111232300",
    "0032311211232300",
    "0032311311332300",
    "0032311111132300",
    "0032311333332300",
    "0003331111333000",
    "0032333333332300",
    "0032322222232300",
    "0031322222231300",
    "0033332222333300",
    "0000323003230000",
    "0003333003333000",
    "0003333003333000"
]

# Down-Right Walk (Frame 1)
GRID_DR_WALK = [
    "0000333333330000",
    "0003222222223000",
    "0032233333322300",
    "0032321111232300",
    "0032311211232300",
    "0032311311332300",
    "0032311111132300",
    "0032311333332300",
    "0003331111333000",
    "0032333333332300",
    "0032322222232300",
    "0031322222231300",
    "0033332222333300",
    "0000320002300000",
    "0003330033300000",
    "0003330033300000"
]

# Up-Right Stand (Frame 4 in final list)
GRID_UR_STAND = [
    "0000333333330000",
    "0003222222223000",
    "0032233333322300",
    "0032222222222300",
    "0032222222222300",
    "0032222222222300",
    "0032222222222300",
    "0032222222222300",
    "0003333333333000",
    "0032333333332300",
    "0032322222232300",
    "0031322222231300",
    "0033332222333300",
    "0000323003230000",
    "0003333003333000",
    "0003333003333000"
]

# Up-Right Walk (Frame 5 in final list)
GRID_UR_WALK = [
    "0000333333330000",
    "0003222222223000",
    "0032233333322300",
    "0032222222222300",
    "0032222222222300",
    "0032222222222300",
    "0032222222222300",
    "0032222222222300",
    "0003333333333000",
    "0032333333332300",
    "0032322222232300",
    "0031322222231300",
    "0033332222333300",
    "0000320002300000",
    "0003330033300000",
    "0003330033300000"
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

def generate_gameover():
    # 80x16 pixels
    img = Image.new("P", (80, 16), 3)
    img.putpalette(PALETTE)
    
    # We can design each letter on an 8x16 grid
    # Let's specify the pixel grids (16 rows of 8 chars)
    # 0: White (text body), 2: Dark Gray (text outline/shadow), 3: Black (background)
    grids = {
        'G': [
            "33322223",
            "33200002",
            "32002222",
            "32023333",
            "32023222",
            "32023202",
            "32002202",
            "33200002",
            "33322223",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333"
        ],
        'A': [
            "33322333",
            "33200233",
            "32022023",
            "32022023",
            "32000023",
            "32022023",
            "32022023",
            "32022023",
            "32233223",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333"
        ],
        'M': [
            "32233223",
            "32022023",
            "32000023",
            "32022023",
            "32022023",
            "32022023",
            "32022023",
            "32022023",
            "32233223",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333"
        ],
        'E': [
            "32222223",
            "32000002",
            "32022222",
            "32000023",
            "32022222",
            "32023333",
            "32000002",
            "32222223",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333"
        ],
        ' ': [
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333"
        ],
        'O': [
            "33222233",
            "32000023",
            "32022023",
            "32022023",
            "32022023",
            "32022023",
            "32000023",
            "33222233",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333"
        ],
        'V': [
            "32233223",
            "32022023",
            "32022023",
            "32022023",
            "32022023",
            "32022023",
            "33200233",
            "33322333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333"
        ],
        'R': [
            "32222233",
            "32000023",
            "32022023",
            "32000233",
            "32022023",
            "32022023",
            "32022023",
            "32233223",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333",
            "33333333"
        ]
    }
    
    text = "GAME OVER"
    for i, char in enumerate(text):
        grid = grids[char]
        for y in range(16):
            for x in range(8):
                val = int(grid[y][x])
                target_x = i * 8 + x + 4
                target_y = y + 3
                if target_x < 80 and target_y < 16:
                    img.putpixel((target_x, target_y), val)
                
    img.save("gameover.png")

def generate_victory():
    img = Image.new("P", (56, 16), 3)
    img.putpalette(PALETTE)
    
    grids = {
        'V': [
            "32223222",
            "32023202",
            "32023202",
            "32023202",
            "33202023",
            "33200023",
            "33320233",
            "33332333"
        ],
        'I': [
            "33222233",
            "33200233",
            "33320233",
            "33320233",
            "33320233",
            "33320233",
            "33200233",
            "33222233"
        ],
        'C': [
            "33222233",
            "32000023",
            "32022233",
            "32023333",
            "32023333",
            "32022233",
            "32000023",
            "33222233"
        ],
        'T': [
            "32222223",
            "32000002",
            "33320233",
            "33320233",
            "33320233",
            "33320233",
            "33320233",
            "33322233"
        ],
        'O': [
            "33222233",
            "32000023",
            "32022023",
            "32022023",
            "32022023",
            "32022023",
            "32000023",
            "33222233"
        ],
        'R': [
            "32222233",
            "32000023",
            "32022023",
            "32000023",
            "32022023",
            "32023023",
            "32023023",
            "32233223"
        ],
        'Y': [
            "32233223",
            "32023202",
            "33202023",
            "33200023",
            "33320233",
            "33320233",
            "33320233",
            "33322233"
        ]
    }
    
    text = "VICTORY"
    for i, char in enumerate(text):
        grid = grids[char]
        for y in range(8):
            for x in range(8):
                val = int(grid[y][x])
                target_x = i * 8 + x
                target_y = y + 4
                if target_x < 56 and target_y < 16:
                    img.putpixel((target_x, target_y), val)
                
    img.save("victory.png")


if __name__ == "__main__":
    generate_tiles()
    generate_player()
    generate_gameover()
    generate_stamina()
    generate_victory()
    print("PNG assets generated (tiles, player, gameover, stamina, victory).")
