import numpy as np
from PIL import Image, ImageDraw

# Game Boy Hardware Colors (Green Palette)
C0 = (224, 248, 207, 255)
C1 = (134, 192, 108, 255)
C2 = (48, 104, 80, 255)
C3 = (7, 24, 33, 255)
TR = (224, 248, 207, 0) # Transparent

# Scarier diagonal ghost
# Down-Right Stand
GHOST_DR_STAND = [
    "0000033333000000",
    "0000322222300000",
    "0003211111230000",
    "0003113113130000",
    "0003112221130000",
    "0031113331130000",
    "0032111211133000",
    "0003211111111300",
    "0000322111113000",
    "0000322111330000",
    "0000032213000000",
    "0000032213000000",
    "0000032113000000",
    "0000321330000000",
    "0000033000000000",
    "0000000000000000"
]

GHOST_DR_WALK = [
    "0000033333000000",
    "0000322222300000",
    "0003211111230000",
    "0003113113130000",
    "0003112221130000",
    "0003113331130000",
    "0032111211133000",
    "0032211111111300",
    "0003221111113000",
    "0000322111330000",
    "0000032213000000",
    "0000032213000000",
    "0000032113000000",
    "0000003213000000",
    "0000000330000000",
    "0000000000000000"
]

GHOST_UR_STAND = [
    "0000033333000000",
    "0000322222300000",
    "0003211111230000",
    "0003111111130000",
    "0003111111130000",
    "0003111111130000",
    "0003211111133000",
    "0000321111111300",
    "0000322111113000",
    "0000322111330000",
    "0000032213000000",
    "0000032213000000",
    "0000032113000000",
    "0000321330000000",
    "0000033000000000",
    "0000000000000000"
]

GHOST_UR_WALK = [
    "0000033333000000",
    "0000322222300000",
    "0003211111230000",
    "0003111111130000",
    "0003111111130000",
    "0003111111130000",
    "0003211111133000",
    "0000321111111300",
    "0000322111113000",
    "0000322111330000",
    "0000032213000000",
    "0000032213000000",
    "0000032113000000",
    "0000003213000000",
    "0000000330000000",
    "0000000000000000"
]

def draw_frame(draw, grid, x_off):
    for y in range(16):
        for x in range(16):
            val = int(grid[y][x])
            draw.point((x_off + x, y), fill=val)

ghost_img = Image.new("P", (128, 16), 0)
PALETTE = [C0[0], C0[1], C0[2], C1[0], C1[1], C1[2], C2[0], C2[1], C2[2], C3[0], C3[1], C3[2]] + [0]*756
ghost_img.putpalette(PALETTE)

dr_s = Image.new("P", (16, 16), 0); draw_frame(ImageDraw.Draw(dr_s), GHOST_DR_STAND, 0)
dr_w = Image.new("P", (16, 16), 0); draw_frame(ImageDraw.Draw(dr_w), GHOST_DR_WALK, 0)
ur_s = Image.new("P", (16, 16), 0); draw_frame(ImageDraw.Draw(ur_s), GHOST_UR_STAND, 0)
ur_w = Image.new("P", (16, 16), 0); draw_frame(ImageDraw.Draw(ur_w), GHOST_UR_WALK, 0)

dl_s = dr_s.transpose(Image.FLIP_LEFT_RIGHT)
dl_w = dr_w.transpose(Image.FLIP_LEFT_RIGHT)
ul_s = ur_s.transpose(Image.FLIP_LEFT_RIGHT)
ul_w = ur_w.transpose(Image.FLIP_LEFT_RIGHT)

ghost_img.paste(dr_s, (0 * 16, 0))
ghost_img.paste(dr_w, (1 * 16, 0))
ghost_img.paste(dl_s, (2 * 16, 0))
ghost_img.paste(dl_w, (3 * 16, 0))
ghost_img.paste(ul_s, (4 * 16, 0))
ghost_img.paste(ul_w, (5 * 16, 0))
ghost_img.paste(ur_s, (6 * 16, 0))
ghost_img.paste(ur_w, (7 * 16, 0))

# Resize by 4x for easier previewing
ghost_preview = Image.new('RGBA', ghost_img.size)
preview_palette = [TR, C1, C2, C3]
for y in range(ghost_img.size[1]):
    for x in range(ghost_img.size[0]):
        p = ghost_img.getpixel((x, y))
        ghost_preview.putpixel((x, y), preview_palette[p])

ghost_preview = ghost_preview.resize((128*4, 16*4), Image.Resampling.NEAREST)
ghost_preview.save('ghost_enemy.png')
print("Saved scary diagonal ghost_enemy.png")
