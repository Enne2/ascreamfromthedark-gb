from PIL import Image

# Standard Game Boy palette (same as generate_assets.py)
# 0: White/transparent-for-sprites, 1: Light Gray, 2: Dark Gray, 3: Black
PALETTE = [
    224, 248, 207, # 0
    134, 192, 108, # 1
    48, 104, 80,   # 2
    7, 24, 33      # 3
] + [0] * (256 * 3 - 12)

# 5x7 font, '1' = light pixel (on), drawn with light gray (1) on transparent (0).
GLYPHS = {
    ' ': [
        "00000",
        "00000",
        "00000",
        "00000",
        "00000",
        "00000",
        "00000",
    ],
    'L': [
        "10000",
        "10000",
        "10000",
        "10000",
        "10000",
        "10000",
        "11111",
    ],
    '0': [
        "01110",
        "10001",
        "10011",
        "10101",
        "11001",
        "10001",
        "01110",
    ],
    '1': [
        "00100",
        "01100",
        "00100",
        "00100",
        "00100",
        "00100",
        "01110",
    ],
    '2': [
        "01110",
        "10001",
        "00001",
        "00010",
        "00100",
        "01000",
        "11111",
    ],
    '3': [
        "11110",
        "00001",
        "00001",
        "01110",
        "00001",
        "00001",
        "11110",
    ],
    '4': [
        "00010",
        "00110",
        "01010",
        "10010",
        "11111",
        "00010",
        "00010",
    ],
    '5': [
        "11111",
        "10000",
        "11110",
        "00001",
        "00001",
        "10001",
        "01110",
    ],
    '6': [
        "00110",
        "01000",
        "10000",
        "11110",
        "10001",
        "10001",
        "01110",
    ],
    '7': [
        "11111",
        "00001",
        "00010",
        "00100",
        "01000",
        "10000",
        "10000",
    ],
    '8': [
        "01110",
        "10001",
        "10001",
        "01110",
        "10001",
        "10001",
        "01110",
    ],
    '9': [
        "01110",
        "10001",
        "10001",
        "01111",
        "00001",
        "00010",
        "01100",
    ],
}

# Glyph order in the sprite sheet (top -> bottom). 11 glyphs, each 8x16 = 2 tiles.
# Index i (0-based) occupies tiles (2i, 2i+1) in level_tiles thanks to -keep_duplicate_tiles.
# 0: 'L', 1..10: '0'..'9'. (No blank glyph: hidden digits are moved offscreen instead.)
ORDER = ['L', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

def main():
    # 8x16 per glyph, stacked vertically -> 8 wide x (16*11)=176 tall
    img = Image.new("P", (8, 176), 0)  # transparent background
    img.putpalette(PALETTE)

    for gi, name in enumerate(ORDER):
        glyph = GLYPHS[name]
        y_base = gi * 16
        # Place the 5x7 glyph in the top rows (0..6), columns 1..5.
        for row in range(7):
            line = glyph[row]
            for col in range(5):
                if line[col] == '1':
                    img.putpixel((1 + col, y_base + row), 1)  # light gray
        # Rows 7..15 stay transparent (0)

    img.save("level.png")
    print("Generated level.png (11 glyphs: L, 0-9)")

if __name__ == "__main__":
    main()