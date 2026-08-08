import re

with open("src/render.c", "r") as f:
    content = f.read()

# Let's completely replace the broken stamina display logic
# First find the start
start_idx = content.find("void update_stamina_display(void) {")
# Find the next function or EOF
end_idx = content.find("void update_player_sprite(void) {", start_idx)

if start_idx != -1 and end_idx != -1:
    old_func = content[start_idx:end_idx]
    
    level_ui_impl = """void update_stamina_display(void) {
    if (game_over) {
        for (uint8_t i = 0; i < 5; i++) {
            move_sprite(18 + i, 0, 0);
        }
        for (uint8_t i = 0; i < 4; i++) {
            move_sprite(23 + i, 0, 0);
        }
        return;
    }
    
    move_sprite(18, (uint8_t)(112 + 8), 16);
    move_sprite(19, (uint8_t)(120 + 8), 16);
    move_sprite(20, (uint8_t)(128 + 8), 16);
    move_sprite(21, (uint8_t)(136 + 8), 16);
    move_sprite(22, (uint8_t)(144 + 8), 16);
    
    uint16_t temp = (uint16_t)stamina * 40;
    uint8_t num_pixels = temp / 100;
    
    uint8_t base_tile = tiles_TILE_COUNT;
    
    for (uint8_t i = 0; i < 5; i++) {
        int8_t p = num_pixels - (i * 8);
        if (p >= 8) p = 8;
        if (p < 0) p = 0;
        
        uint8_t t = base_tile;
        if (i == 0) {
            t += (p == 8) ? 2 : (p > 0 ? 0 : 0);
        } else if (i == 4) {
            t += (p == 8) ? 6 : (p > 0 ? 4 : 4);
        } else {
            t += (p == 8) ? 8 : (p > 0 ? 8 : 8); 
        }
        
        set_sprite_tile(18 + i, t);
        set_sprite_prop(18 + i, 0);
    }

    // DRAW LEVEL UI
    uint8_t level_base_tile = tiles_TILE_COUNT + stamina_TILE_COUNT * 2;
    uint8_t tens = current_level / 10;
    uint8_t ones = current_level % 10;
    
    set_sprite_tile(23, level_base_tile);
    set_sprite_tile(24, level_base_tile + 2);
    set_sprite_tile(25, level_base_tile + 4 + tens * 2);
    set_sprite_tile(26, level_base_tile + 4 + ones * 2);
    
    move_sprite(23, 8 + 0, 16);
    move_sprite(24, 8 + 8, 16);
    move_sprite(25, 8 + 16, 16);
    move_sprite(26, 8 + 24, 16);
}

"""
    content = content[:start_idx] + level_ui_impl + content[end_idx:]

with open("src/render.c", "w") as f:
    f.write(content)
