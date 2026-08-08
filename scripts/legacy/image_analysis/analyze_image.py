from PIL import Image
img = Image.open('assets/next_level_original.png')
colors = img.getcolors()
print(f"Number of colors: {len(colors) if colors else 'too many'}")
