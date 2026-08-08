import re

with open("src/engine.c", "r") as f:
    content = f.read()

content = content.replace("set_sprite_data(tiles_TILE_COUNT, stamina_TILE_COUNT * 2, stamina_tiles);", 
                          "set_sprite_data(tiles_TILE_COUNT, stamina_TILE_COUNT, stamina_tiles);")

content = content.replace("set_sprite_data(tiles_TILE_COUNT + stamina_TILE_COUNT * 2, 24, level_ui_tiles);", 
                          "set_sprite_data(tiles_TILE_COUNT + stamina_TILE_COUNT, level_ui_TILE_COUNT, level_ui_tiles);")

with open("src/engine.c", "w") as f:
    f.write(content)


with open("src/render.c", "r") as f:
    content = f.read()

content = content.replace("uint8_t level_base_tile = tiles_TILE_COUNT + stamina_TILE_COUNT * 2;", 
                          "uint8_t level_base_tile = tiles_TILE_COUNT + stamina_TILE_COUNT;")

with open("src/render.c", "w") as f:
    f.write(content)
