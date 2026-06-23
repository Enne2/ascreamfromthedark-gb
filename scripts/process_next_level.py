from PIL import Image

img = Image.open('assets/next_level.png').convert('L') # Convert to grayscale
img = img.quantize(colors=4) # Quantize to 4 colors
img = img.convert('RGB')
# Force colors to exactly GB shades
palette = [(224, 248, 208), (136, 192, 112), (52, 104, 86), (8, 24, 32)]
# Actually the game uses generic colors or grayscale. Let's use 4 grayscale values:
gb_palette = [(255,255,255), (170,170,170), (85,85,85), (0,0,0)]

new_img = Image.new('RGB', img.size)
for y in range(img.height):
    for x in range(img.width):
        p = img.getpixel((x, y))
        # Find closest color in gb_palette
        best_c = gb_palette[0]
        min_dist = 1000000
        for c in gb_palette:
            dist = (p[0]-c[0])**2 + (p[1]-c[1])**2 + (p[2]-c[2])**2
            if dist < min_dist:
                min_dist = dist
                best_c = c
        new_img.putpixel((x, y), best_c)

new_img.save('assets/next_level.png')
print("Processed next_level.png")
