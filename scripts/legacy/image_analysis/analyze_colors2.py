from PIL import Image
img = Image.open('assets/next_level.png').convert('RGB')
colors = img.getcolors(10000)
if colors:
    colors.sort(reverse=True)
    print("Top colors in quantized:")
    for count, color in colors[:10]:
        print(f"{color}: {count}")
