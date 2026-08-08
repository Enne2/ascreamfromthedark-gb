import re

with open("src/engine.c", "r") as f:
    content = f.read()

# Replace MAP_SIZE
content = content.replace("MAP_SIZE", "current_map_size")

# Inject init_enemies and map size reset
content = content.replace("void engine_init(void) {\n    game_over = 0;", "void engine_init(void) {\n    current_level = 1;\n    current_map_size = 7;\n    game_over = 0;")

enemy_spawn_regex = r'// SPAWN DEL NEMICO.*?enemy_target_py = 0;'
content = re.sub(enemy_spawn_regex, "init_enemies();", content, flags=re.DOTALL)

# Add headers
if '#include "enemy_logic.h"' not in content:
    content = content.replace('#include "enemy.h"', '#include "enemy.h"\n#include "enemy_logic.h"\n#include "level_ui.h"')
if '#include "level_ui.h"' not in content:
    content = content.replace('#include "enemy_logic.h"', '#include "enemy_logic.h"\n#include "level_ui.h"')

# Add level_ui tiles load
sprite_data_str = "set_sprite_data(tiles_TILE_COUNT, stamina_TILE_COUNT * 2, stamina_tiles);"
if "level_ui_tiles" not in content:
    new_sprite_data = sprite_data_str + "\n    set_sprite_data(tiles_TILE_COUNT + stamina_TILE_COUNT * 2, 24, level_ui_tiles);"
    content = content.replace(sprite_data_str, new_sprite_data)

# Replace victory logic
victory_regex = r'// --- GESTIONE STATO DI FINE GIOCO.*?// --- GESTIONE DEL LOOP DI GIOCO STANDARD ---'

new_victory = """// --- GESTIONE STATO DI FINE GIOCO (Sconfitta o Vittoria) ---
    if (game_over) {
        if (game_over_timer > 0) {
            game_over_timer--;
            // Quando scade il timer drammatico...
            if (game_over_timer == 0) {
                if (game_over == 1) {
                    // ...Svuota lo schermo
                    memset(map_buffer, 0, sizeof(map_buffer));
                    set_bkg_tiles(0, 0, 32, 32, map_buffer);
                    
                    NR21_REG = 0x80;
                    NR22_REG = 0xF3; 
                    NR23_REG = 0x2C; 
                    NR24_REG = 0x84;
                } else if (game_over == 2) {
                    current_level++;
                    if (current_level >= 26) {
                        app_state = 2; // Victory!
                        return;
                    } else {
                        current_map_size++;
                        if (current_map_size > 32) current_map_size = 32;
                        
                        game_over = 0;
                        generate_maze();
                        
                        player_lx = 1;
                        player_ly = 1;
                        if (maze[player_ly][player_lx] == 0) {
                            uint8_t found = 0;
                            for (uint8_t y = 1; y < current_map_size - 1; y++) {
                                for (uint8_t x = 1; x < current_map_size - 1; x++) {
                                    if (maze[y][x] == 1) {
                                        player_lx = x;
                                        player_ly = y;
                                        found = 1;
                                        break;
                                    }
                                }
                                if (found) break;
                            }
                        }
                        
                        is_moving = 0;
                        is_jumping = 0;
                        stamina = 100;
                        scroll_x = 0;
                        scroll_y = 0;
                        
                        init_enemies();
                        
                        sound_reset_music_state();
                    }
                }
            }
        } else {
            // Dopo il timer
            if (game_over == 1) {
                move_metasprite(gameover_metasprites[0], player_TILE_COUNT + enemy_TILE_COUNT, 8, 88, 120);
            }
            
            update_player_sprite();
            
            // Hide enemies since game is over
            for (uint8_t i = 0; i < num_enemies; i++) {
                int16_t enemy_px = (enemy_lx[i] - enemy_ly[i]) * 16 + 96;
                int16_t enemy_py = (enemy_lx[i] + enemy_ly[i]) * 8 + 16;
                int16_t enemy_screen_x = ((enemy_px - scroll_x) & 255) + 24;
                int16_t enemy_screen_y = ((enemy_py - scroll_y) & 255) + 16;
                
                int8_t edx = (int8_t)player_lx - (int8_t)enemy_lx[i];
                int8_t edy = (int8_t)player_ly - (int8_t)enemy_ly[i];
                if (edx < 0) edx = -edx;
                if (edy < 0) edy = -edy;
                uint8_t ep_dist = (edx > edy) ? edx : edy;
                
                if (game_over == 1 && ep_dist <= 2 && enemy_screen_x >= -8 && enemy_screen_x <= 168 && enemy_screen_y >= -8 && enemy_screen_y <= 152) {
                    if (i == 0) {
                        move_metasprite(enemy_metasprites[0], player_TILE_COUNT, 4, enemy_screen_x, enemy_screen_y);
                    }
                } else {
                    move_metasprite(enemy_metasprites[0], player_TILE_COUNT, 4 + i * 4, 0, 0); 
                }
            }

            if ((keys & J_START) && !(prev_keys & J_START)) {
                move_metasprite(gameover_metasprites[0], player_TILE_COUNT + enemy_TILE_COUNT, 8, 0, 0);
                SHOW_SPRITES;
                engine_init();
            }
        }
        return;
    }

    // --- GESTIONE DEL LOOP DI GIOCO STANDARD ---"""

content = re.sub(victory_regex, new_victory, content, flags=re.DOTALL)

with open("src/engine.c", "w") as f:
    f.write(content)
