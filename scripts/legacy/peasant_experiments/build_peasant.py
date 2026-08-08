import numpy as np
from PIL import Image, ImageDraw

PALETTE = [
    224, 248, 207, # 0
    134, 192, 108, # 1
    48, 104, 80,   # 2
    7, 24, 33      # 3
] + [0] * (256 * 3 - 12)

# Based on peasant_preview3, but looking down-right
GRID_DR_STAND = [
    "0000333333330000",
    "0003222222223000",
    "0032233333322300",
    "0032321111232300",
    "0032312112132300",
    "0032313113132300",
    "0032311111132300",
    "0032313333132300",
    "0003331111333000",
    "0032333333332300",
    "0032322222232300",
    "0031322222231300",
    "0033332222333300",
    "0000323003230000",
    "0003333003333000",
    "0003333003333000"
]

def draw_frame(draw, grid, x_off):
    for y in range(16):
        for x in range(16):
            val = int(grid[y][x])
            draw.point((x_off + x, y), fill=val)

img = Image.new("P", (16, 16), 0)
img.putpalette(PALETTE)
draw_frame(ImageDraw.Draw(img), GRID_DR_STAND, 0)
img.save("test_peasant.png")
