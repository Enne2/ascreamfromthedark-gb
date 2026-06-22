from PIL import Image

# Open the new cover image
img = Image.open('bg.png')

# Resize to 128x128 to ensure maximum 256 unique tiles
img = img.resize((128, 128), Image.Resampling.LANCZOS)

# Create a black 160x144 background
bg = Image.new('L', (160, 144), color=0)

# Paste the resized image in the center
bg.paste(img, (16, 8))

# Quantize to 4 colors (indexed mode 'P') for png2asset
final_img = bg.quantize(colors=4)

# Save the resulting image
final_img.save('title_bg.png')
print("title_bg.png created successfully (160x144, indexed).")


