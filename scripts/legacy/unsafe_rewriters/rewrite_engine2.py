import re

with open("src/engine.c", "r") as f:
    content = f.read()

# Add include
content = content.replace('#include "stamina.h"', '#include "stamina.h"\n#include "level_ui.h"')

# Add set_sprite_data
sprite_data_str = "set_sprite_data(tiles_TILE_COUNT, stamina_TILE_COUNT * 2, stamina_tiles);"
new_sprite_data = sprite_data_str + "\n    set_sprite_data(tiles_TILE_COUNT + stamina_TILE_COUNT * 2, 12, level_ui_tiles);"
content = content.replace(sprite_data_str, new_sprite_data)

with open("src/engine.c", "w") as f:
    f.write(content)
