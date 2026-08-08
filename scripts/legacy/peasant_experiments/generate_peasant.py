import numpy as np
from PIL import Image

palette = [
    (224, 248, 207, 0),    # 0: Transparent (alpha 0, but Game Boy color 0)
    (134, 192, 108, 255),  # 1: Light
    (48, 104, 80, 255),    # 2: Dark
    (7, 24, 33, 255)       # 3: Black
]

sprite = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], # 00
    [0,0,0,3,1,3,0,0,0,0,0,0,0,0,0,0], # 01 flame tip
    [0,0,3,1,2,1,3,0,0,3,3,3,3,3,0,0], # 02 flame / head top
    [0,0,3,1,2,1,3,0,3,2,2,2,2,2,3,0], # 03 flame / hood
    [0,0,0,3,1,3,0,0,3,1,1,1,1,1,3,0], # 04 flame base / face top
    [0,0,0,3,2,3,0,0,3,1,3,1,3,1,3,0], # 05 stick / scared eyes (wide)
    [0,0,0,3,2,3,0,0,3,1,1,3,1,1,3,0], # 06 stick / scared open mouth
    [0,0,0,3,2,3,0,0,0,3,1,1,1,3,0,0], # 07 stick / chin
    [0,0,0,3,2,3,0,0,3,2,2,2,2,2,3,0], # 08 stick / shoulders
    [0,0,3,1,1,1,3,3,2,2,2,2,2,3,0,0], # 09 hand holding stick / body
    [0,0,0,3,3,3,0,3,2,2,2,2,2,3,1,3], # 10 hand bottom / body / right hand
    [0,0,0,0,0,0,0,0,3,2,2,2,2,3,3,3], # 11 body lower
    [0,0,0,0,0,0,0,0,3,2,3,0,3,2,3,0], # 12 legs
    [0,0,0,0,0,0,0,0,3,2,3,0,3,2,3,0], # 13 legs
    [0,0,0,0,0,0,0,3,3,2,3,0,3,2,3,3], # 14 shoes
    [0,0,0,0,0,0,0,3,3,3,0,0,0,3,3,3], # 15 shoes bottom
]

img = Image.new('RGBA', (16, 16))
pixels = img.load()
for y in range(16):
    for x in range(16):
        pixels[x, y] = palette[sprite[y][x]]

# Save 16x16 with transparency (for the actual asset generation)
img.save('peasant_16x16.png')

# Upscale for preview
preview = img.resize((160, 160), Image.Resampling.NEAREST)
bg = Image.new('RGBA', (160, 160), (224, 248, 207, 255))
bg.paste(preview, (0,0), preview)
bg.save('peasant_preview.png')
print("Generated peasant_16x16.png and peasant_preview.png")
