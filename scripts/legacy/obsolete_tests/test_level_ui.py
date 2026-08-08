from PIL import Image, ImageDraw
PALETTE = [224, 248, 207, 134, 192, 108, 48, 104, 80, 7, 24, 33] + [0]*756
img = Image.new("P", (96, 8), 3)
img.putpalette(PALETTE)
draw = ImageDraw.Draw(img)
draw.text((0, 0), "LV", fill=0)
for i in range(10):
    draw.text((16 + i * 8 + 2, 0), str(i), fill=0)
img.save("assets/level_ui.png")
