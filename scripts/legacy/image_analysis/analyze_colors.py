from PIL import Image
img = Image.open('assets/next_level_original.png').convert('RGB')
colors = img.getcolors(10000)
if colors:
    # sort by count
    colors.sort(reverse=True)
    print("Top 10 colors:")
    for count, color in colors[:10]:
        print(f"{color}: {count}")
else:
    print("Too many colors")
