from PIL import Image

# Open the new cover image
img = Image.open('bg.png')

# Convert to grayscale first to get raw intensity values
img_gray = img.convert('L')

# Create a new indexed image with the exact Game Boy palette mapping
# 0 = White, 1 = Light Gray, 2 = Dark Gray, 3 = Black
final_img = Image.new('P', img_gray.size)

# Set the palette
palette = [
    255, 255, 255, # 0: White
    170, 170, 170, # 1: Light Gray
    85,  85,  85,  # 2: Dark Gray
    0,   0,   0    # 3: Black
]
palette += [0] * (256 * 3 - len(palette))
final_img.putpalette(palette)

# Map the grayscale pixels to palette indices (0-3)
# Darker pixels get higher indices (closer to 3/Black), lighter get lower indices (closer to 0/White)
raw_pixels = list(img_gray.getdata())
mapped_pixels = []
for p in raw_pixels:
    if p > 200:
        mapped_pixels.append(0) # White
    elif p > 120:
        mapped_pixels.append(1) # Light Gray
    elif p > 55:
        mapped_pixels.append(2) # Dark Gray
    else:
        mapped_pixels.append(3) # Black

final_img.putdata(mapped_pixels)

# Save the resulting image
final_img.save('title_bg.png')
print("title_bg.png created successfully with correct color indexing.")


