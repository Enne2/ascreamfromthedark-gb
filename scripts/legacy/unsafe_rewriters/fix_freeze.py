with open("src/engine.c", "r") as f:
    content = f.read()

content = content.replace("init_enemies();\n                        \n                        sound_reset_music_state();", 
                          "init_enemies();\n                        \n                        draw_map(player_lx, player_ly);\n                        update_camera();\n                        \n                        sound_reset_music_state();")

with open("src/engine.c", "w") as f:
    f.write(content)
