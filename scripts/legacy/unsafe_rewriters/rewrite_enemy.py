import re

with open("src/enemy_logic.c", "r") as f:
    content = f.read()

new_logic = """void init_enemies(void) {
    num_enemies = 1 + (current_level / 5);
    if (num_enemies > MAX_ENEMIES) num_enemies = MAX_ENEMIES;
    
    // Spawn enemies far from the player
    for (uint8_t i = 0; i < num_enemies; i++) {
        enemy_is_moving[i] = 0;
        enemy_cooldown[i] = 0;
        while (1) {
            uint8_t rx = 1 + (rand() % (current_map_size - 2));
            uint8_t ry = 1 + (rand() % (current_map_size - 2));
            if (maze[ry][rx] == 1) {
                // Must be at least 3 tiles away from player
                int8_t dx = (int8_t)rx - (int8_t)player_lx;
                int8_t dy = (int8_t)ry - (int8_t)player_ly;
                if (dx < 0) dx = -dx;
                if (dy < 0) dy = -dy;
                if (dx + dy > 4) {
                    enemy_lx[i] = rx;
                    enemy_ly[i] = ry;
                    break;
                }
            }
        }
    }
}

void update_enemy_logic(void) {
    uint8_t next_oam_idx = 4; // Sprites 0-3 are player

    int16_t p_px = is_moving ? (start_px + (((target_px - start_px) * (int16_t)move_progress) >> 4)) : ((player_lx - player_ly) * 16 + 96);
    int16_t p_py = is_moving ? (start_py + (((target_py - start_py) * (int16_t)move_progress) >> 4)) : ((player_lx + player_ly) * 8 + 16);

    for (uint8_t i = 0; i < num_enemies; i++) {
        // 1. Update visual interpolation
        if (enemy_is_moving[i]) {
            enemy_move_progress[i]++;
            if (enemy_move_progress[i] == 16) {
                enemy_is_moving[i] = 0;
                enemy_lx[i] = enemy_target_lx[i];
                enemy_ly[i] = enemy_target_ly[i];
                enemy_cooldown[i] = 60; 
            }
        }

        // 2. Cooldown
        if (enemy_cooldown[i] > 0) {
            enemy_cooldown[i]--;
        }

        // 3. AI Pathfinding
        if (!enemy_is_moving[i] && enemy_cooldown[i] == 0) {
            int8_t dx = (int8_t)player_lx - (int8_t)enemy_lx[i];
            int8_t dy = (int8_t)player_ly - (int8_t)enemy_ly[i];
            int8_t abs_dx = (dx < 0) ? -dx : dx;
            int8_t abs_dy = (dy < 0) ? -dy : dy;
            int8_t dist = (abs_dx > abs_dy) ? abs_dx : abs_dy;
            
            if (dist <= 3) { // Wake up if within 3 cells
                int8_t best_nx = enemy_lx[i];
                int8_t best_ny = enemy_ly[i];
                int16_t min_dist_sq = (int16_t)dx * dx + (int16_t)dy * dy;
                
                if (enemy_lx[i] + 1 < current_map_size && maze[enemy_ly[i]][enemy_lx[i] + 1] != 0) {
                    int8_t ndx = (int8_t)player_lx - (int8_t)(enemy_lx[i] + 1);
                    int8_t ndy = (int8_t)player_ly - (int8_t)enemy_ly[i];
                    int16_t d_sq = (int16_t)ndx * ndx + (int16_t)ndy * ndy;
                    if (d_sq < min_dist_sq) { min_dist_sq = d_sq; best_nx = enemy_lx[i] + 1; best_ny = enemy_ly[i]; }
                }
                if (enemy_ly[i] + 1 < current_map_size && maze[enemy_ly[i] + 1][enemy_lx[i]] != 0) {
                    int8_t ndx = (int8_t)player_lx - (int8_t)enemy_lx[i];
                    int8_t ndy = (int8_t)player_ly - (int8_t)(enemy_ly[i] + 1);
                    int16_t d_sq = (int16_t)ndx * ndx + (int16_t)ndy * ndy;
                    if (d_sq < min_dist_sq) { min_dist_sq = d_sq; best_nx = enemy_lx[i]; best_ny = enemy_ly[i] + 1; }
                }
                if (enemy_lx[i] > 0 && maze[enemy_ly[i]][enemy_lx[i] - 1] != 0) {
                    int8_t ndx = (int8_t)player_lx - (int8_t)(enemy_lx[i] - 1);
                    int8_t ndy = (int8_t)player_ly - (int8_t)enemy_ly[i];
                    int16_t d_sq = (int16_t)ndx * ndx + (int16_t)ndy * ndy;
                    if (d_sq < min_dist_sq) { min_dist_sq = d_sq; best_nx = enemy_lx[i] - 1; best_ny = enemy_ly[i]; }
                }
                if (enemy_ly[i] > 0 && maze[enemy_ly[i] - 1][enemy_lx[i]] != 0) {
                    int8_t ndx = (int8_t)player_lx - (int8_t)enemy_lx[i];
                    int8_t ndy = (int8_t)player_ly - (int8_t)(enemy_ly[i] - 1);
                    int16_t d_sq = (int16_t)ndx * ndx + (int16_t)ndy * ndy;
                    if (d_sq < min_dist_sq) { min_dist_sq = d_sq; best_nx = enemy_lx[i]; best_ny = enemy_ly[i] - 1; }
                }
                
                if (best_nx != (int8_t)enemy_lx[i] || best_ny != (int8_t)enemy_ly[i]) {
                    enemy_is_moving[i] = 1;
                    enemy_move_progress[i] = 0;
                    enemy_start_lx[i] = enemy_lx[i];
                    enemy_start_ly[i] = enemy_ly[i];
                    enemy_target_lx[i] = best_nx;
                    enemy_target_ly[i] = best_ny;
                    
                    enemy_start_px[i] = (enemy_start_lx[i] - enemy_start_ly[i]) * 16 + 96;
                    enemy_start_py[i] = (enemy_start_lx[i] + enemy_start_ly[i]) * 8 + 16;
                    enemy_target_px[i] = (enemy_target_lx[i] - enemy_target_ly[i]) * 16 + 96;
                    enemy_target_py[i] = (enemy_target_lx[i] + enemy_target_ly[i]) * 8 + 16;
                }
            }
        }

        // 4. RENDERING & COLLISION
        int16_t enemy_px, enemy_py;
        if (enemy_is_moving[i]) {
            enemy_px = enemy_start_px[i] + (((enemy_target_px[i] - enemy_start_px[i]) * (int16_t)enemy_move_progress[i]) >> 4);
            enemy_py = enemy_start_py[i] + (((enemy_target_py[i] - enemy_start_py[i]) * (int16_t)enemy_move_progress[i]) >> 4);
        } else {
            enemy_px = (enemy_lx[i] - enemy_ly[i]) * 16 + 96;
            enemy_py = (enemy_lx[i] + enemy_ly[i]) * 8 + 16;
        }
        
        int16_t enemy_screen_x = ((enemy_px - scroll_x) & 255) + 24;
        int16_t enemy_screen_y = ((enemy_py - scroll_y) & 255) + 16;
        
        int8_t edx = (int8_t)player_lx - (int8_t)enemy_lx[i];
        int8_t edy = (int8_t)player_ly - (int8_t)enemy_ly[i];
        if (edx < 0) edx = -edx;
        if (edy < 0) edy = -edy;
        uint8_t ep_dist = (edx > edy) ? edx : edy;
        
        // Draw up to 3 enemies (sprites 4-15)
        if (ep_dist <= 2 && enemy_screen_x >= -8 && enemy_screen_x <= 168 && enemy_screen_y >= -8 && enemy_screen_y <= 152) {
            if (next_oam_idx <= 14) {
                move_metasprite(enemy_metasprites[0], player_TILE_COUNT, next_oam_idx, enemy_screen_x, enemy_screen_y); 
                next_oam_idx += 4;
            }
        }
        
        if (game_over == 0) {
            int16_t dx_p = p_px - enemy_px;
            int16_t dy_p = p_py - enemy_py;
            if (dx_p < 0) dx_p = -dx_p;
            if (dy_p < 0) dy_p = -dy_p;
            
            if (dx_p < 8 && dy_p < 6 && (is_jumping == 0)) {
                game_over = 1;
                game_over_timer = 60; 
                NR52_REG = 0x80;
                NR50_REG = 0x77;
                NR51_REG = 0xFF;
                NR10_REG = 0x16;
                NR11_REG = 0x40;
                NR12_REG = 0x73;
                NR13_REG = 0x00;
                NR14_REG = 0xC3;
            }
        }
    }

    // Hide unused enemy sprites
    while (next_oam_idx <= 14) {
        move_metasprite(enemy_metasprites[0], player_TILE_COUNT, next_oam_idx, 0, 0); 
        next_oam_idx += 4;
    }
}
"""

content = re.sub(r'void update_enemy_logic\(void\) \{.*', new_logic, content, flags=re.DOTALL)

with open("src/enemy_logic.c", "w") as f:
    f.write(content)
