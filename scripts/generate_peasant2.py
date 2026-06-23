import numpy as np
from PIL import Image

palette = [
    (224, 248, 207, 0),    # 0: Transparent
    (134, 192, 108, 255),  # 1: Light (Skin)
    (48, 104, 80, 255),    # 2: Dark (Clothes/Hood)
    (7, 24, 33, 255)       # 3: Black (Outlines/Eyes)
]

sprite = [
    [0,0,0,0, 3,3,3,3,3,3,3,3, 0,0,0,0], # 00 hat top
    [0,0,0,3, 2,2,2,2,2,2,2,2, 3,0,0,0], # 01 hat
    [0,0,3,2, 2,3,3,3,3,3,3,2, 2,3,0,0], # 02 hat brim
    [0,0,3,2, 3,2,1,1,1,1,2,3, 2,3,0,0], # 03 eyebrows outer
    [0,0,3,2, 3,1,2,1,1,2,1,3, 2,3,0,0], # 04 eyebrows inner
    [0,0,3,2, 3,1,3,1,1,3,1,3, 2,3,0,0], # 05 eyes
    [0,0,3,2, 3,1,1,3,3,1,1,3, 2,3,0,0], # 06 mouth
    [0,0,3,2, 3,1,1,3,3,1,1,3, 2,3,0,0], # 07 mouth
    [0,0,0,3, 3,3,1,1,1,1,3,3, 3,0,0,0], # 08 chin
    [0,0,3,2, 2,3,3,3,3,3,3,2, 2,3,0,0], # 09 shoulders
    [0,0,3,2, 2,3,1,1,1,1,3,2, 2,3,0,0], # 10 hands clasped
    [0,0,3,2, 2,3,3,3,3,3,3,2, 2,3,0,0], # 11 belt/lower arms
    [0,0,3,2, 2,2,2,2,2,2,2,2, 2,3,0,0], # 12 tunic
    [0,0,0,3, 2,2,2,3,3,2,2,2, 3,0,0,0], # 13 tunic split
    [0,0,0,0, 3,2,3,0,0,3,2,3, 0,0,0,0], # 14 legs
    [0,0,0,3, 3,3,3,0,0,3,3,3, 3,0,0,0], # 15 shoes
]

# We need to replace the first frame of player.png which is 128x16
# We will create a new 128x16 image, paste this frame into the first slot
# For now, we just copy this frame 8 times so the animation doesn't break, 
# although we only designed the first frame. 
img_sheet = Image.new('P', (128, 16))
# Create palette flat array
flat_palette = []
for p in palette:
    flat_palette.extend([p[0], p[1], p[2]])
# Pad palette to 256 colors
flat_palette.extend([0] * (768 - len(flat_palette)))
img_sheet.putpalette(flat_palette)

pixels = img_sheet.load()

for frame in range(8):
    for y in range(16):
        for x in range(16):
            pixels[x + frame*16, y] = sprite[y][x]

# Save the game asset
img_sheet.save('player.png', transparency=0)

# Save the preview
preview = Image.new('RGBA', (16, 16))
p_pixels = preview.load()
for y in range(16):
    for x in range(16):
        p_pixels[x, y] = palette[sprite[y][x]]

preview = preview.resize((160, 160), Image.Resampling.NEAREST)
bg = Image.new('RGBA', (160, 160), (224, 248, 207, 255))
bg.paste(preview, (0,0), preview)
bg.save('peasant_preview2.png')

print("Generated player.png and peasant_preview2.png")
