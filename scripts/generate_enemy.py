import numpy as np
from PIL import Image, ImageDraw

# Game Boy Hardware Colors (Green Palette)
PALETTE = [
    224, 248, 207, # 0
    134, 192, 108, # 1
    48, 104, 80,   # 2
    7, 24, 33      # 3
] + [0] * (256 * 3 - 12)

# Scarier diagonal ghost
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
ghost_img.putpalette(PALETTE)

dr_s = Image.new("P", (16, 16), 0); dr_s.putpalette(PALETTE); draw_frame(ImageDraw.Draw(dr_s), GHOST_DR_STAND, 0)
dr_w = Image.new("P", (16, 16), 0); dr_w.putpalette(PALETTE); draw_frame(ImageDraw.Draw(dr_w), GHOST_DR_WALK, 0)
ur_s = Image.new("P", (16, 16), 0); ur_s.putpalette(PALETTE); draw_frame(ImageDraw.Draw(ur_s), GHOST_UR_STAND, 0)
ur_w = Image.new("P", (16, 16), 0); ur_w.putpalette(PALETTE); draw_frame(ImageDraw.Draw(ur_w), GHOST_UR_WALK, 0)

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

ghost_img.save('enemy.png')
print("Saved enemy.png")
