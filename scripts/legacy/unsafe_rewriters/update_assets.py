import os

with open('generate_assets.py', 'r') as f:
    content = f.read()

GHOST_GRIDS = """
# Ghost Grids
GHOST_DR_STAND = [
    "0000033333000000",
    "0000322222300000",
    "0003211111230000",
    "0003113113130000",
    "0003112221130000",
    "0031113331130000",
    "0032111211133000",
    "0003211111111300",
    "0000322111113000",
    "0000322111330000",
    "0000032213000000",
    "0000032213000000",
    "0000032113000000",
    "0000321330000000",
    "0000033000000000",
    "0000000000000000"
]

GHOST_DR_WALK = [
    "0000033333000000",
    "0000322222300000",
    "0003211111230000",
    "0003113113130000",
    "0003112221130000",
    "0003113331130000",
    "0032111211133000",
    "0032211111111300",
    "0003221111113000",
    "0000322111330000",
    "0000032213000000",
    "0000032213000000",
    "0000032113000000",
    "0000003213000000",
    "0000000330000000",
    "0000000000000000"
]

GHOST_UR_STAND = [
    "0000033333000000",
    "0000322222300000",
    "0003211111230000",
    "0003111111130000",
    "0003111111130000",
    "0003111111130000",
    "0003211111133000",
    "0000321111111300",
    "0000322111113000",
    "0000322111330000",
    "0000032213000000",
    "0000032213000000",
    "0000032113000000",
    "0000321330000000",
    "0000033000000000",
    "0000000000000000"
]

GHOST_UR_WALK = [
    "0000033333000000",
    "0000322222300000",
    "0003211111230000",
    "0003111111130000",
    "0003111111130000",
    "0003111111130000",
    "0003211111133000",
    "0000321111111300",
    "0000322111113000",
    "0000322111330000",
    "0000032213000000",
    "0000032213000000",
    "0000032113000000",
    "0000003213000000",
    "0000000330000000",
    "0000000000000000"
]

def generate_enemy():
    img = Image.new("P", (128, 16), 0)
    img.putpalette(PALETTE)
    
    dr_s = Image.new("P", (16, 16), 0)
    dr_s.putpalette(PALETTE)
    draw_frame(ImageDraw.Draw(dr_s), GHOST_DR_STAND, 0)
    
    dr_w = Image.new("P", (16, 16), 0)
    dr_w.putpalette(PALETTE)
    draw_frame(ImageDraw.Draw(dr_w), GHOST_DR_WALK, 0)
    
    ur_s = Image.new("P", (16, 16), 0)
    ur_s.putpalette(PALETTE)
    draw_frame(ImageDraw.Draw(ur_s), GHOST_UR_STAND, 0)
    
    ur_w = Image.new("P", (16, 16), 0)
    ur_w.putpalette(PALETTE)
    draw_frame(ImageDraw.Draw(ur_w), GHOST_UR_WALK, 0)
    
    dl_s = dr_s.transpose(Image.FLIP_LEFT_RIGHT)
    dl_w = dr_w.transpose(Image.FLIP_LEFT_RIGHT)
    ul_s = ur_s.transpose(Image.FLIP_LEFT_RIGHT)
    ul_w = ur_w.transpose(Image.FLIP_LEFT_RIGHT)
    
    img.paste(dr_s, (0 * 16, 0))
    img.paste(dr_w, (1 * 16, 0))
    img.paste(dl_s, (2 * 16, 0))
    img.paste(dl_w, (3 * 16, 0))
    img.paste(ul_s, (4 * 16, 0))
    img.paste(ul_w, (5 * 16, 0))
    img.paste(ur_s, (6 * 16, 0))
    img.paste(ur_w, (7 * 16, 0))
    
    img.save("enemy.png")
"""

content = content.replace("def generate_player():", GHOST_GRIDS + "\ndef generate_player():")
content = content.replace("generate_player()", "generate_player()\n    generate_enemy()")
content = content.replace("player, gameover", "player, enemy, gameover")

with open('generate_assets.py', 'w') as f:
    f.write(content)
