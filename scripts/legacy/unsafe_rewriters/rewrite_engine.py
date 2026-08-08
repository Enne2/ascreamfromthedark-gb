import re

with open("src/engine.c", "r") as f:
    content = f.read()

# Replace MAP_SIZE with current_map_size
content = content.replace("MAP_SIZE", "current_map_size")

# Inject current_level = 1 and current_map_size = 7 into engine_init
init_patch = """void engine_init(void) {
    current_level = 1;
    current_map_size = 7;
    game_over = 0;"""
content = re.sub(r'void engine_init\(void\) \{\s*game_over = 0;', init_patch, content)

# Inject init_enemies() and remove old enemy spawn logic
enemy_spawn_regex = r'// SPAWN DEL NEMICO.*?enemy_target_py = 0;'
new_enemy_spawn = "// SPAWN NEMICI\n    init_enemies();"
content = re.sub(enemy_spawn_regex, new_enemy_spawn, content, flags=re.DOTALL)

# Modify victory logic to increment level and map size
victory_reset_regex = r'if \(game_over_timer == 0\) \{\s*if \(game_over == 1\).*?\}'
new_victory_logic = """if (game_over_timer == 0) {
            if (game_over == 1) { // Game Over (Death)
                app_state = 0; // Return to title screen
                title_init();
            } else if (game_over == 2) { // Next Level Reached
                // INcrement level and increase map size!
                current_level++;
                if (current_level >= 26) {
                    // VICTORY! Max level reached
                    // Note: Since we don't have a victory.c anymore, we can just return to title screen
                    // Or we could implement a basic text victory screen. For now, let's reset to title.
                    // The user said: "alla fine il gioco sarà vinto con messaggio apposito e complimente da parte mia"
                    // I will add app_state = 2 for Victory Screen later in engine.c!
                    app_state = 2; // WE WILL ADD A VICTORY STATE!
                    // title_init();
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
                    
                    play_music_tick(0);
                }
            }
        }"""
content = re.sub(victory_reset_regex, new_victory_logic, content, flags=re.DOTALL)

# Add #include "enemy_logic.h" at the top
if '#include "enemy_logic.h"' not in content:
    content = content.replace('#include "enemy.h"', '#include "enemy.h"\n#include "enemy_logic.h"')

with open("src/engine.c", "w") as f:
    f.write(content)
