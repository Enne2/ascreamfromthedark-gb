#ifndef GLOBALS_H
#define GLOBALS_H

#include <stdint.h>

/**
 * ==========================================
 * GLOBAL GAME STATE
 * ==========================================
 * Shared variables across modules (rendering, player, enemy, audio).
 * Centralized here to avoid circular dependencies in C.
 */

// --- General Application State ---
// app_state = 0 means Title Screen, 1 means Gameplay
extern uint8_t app_state;

// game_over: 0 = Playing, 1 = Defeat (caught), 2 = Victory/Going Deeper (next level),
//            3 = Finale (cleared level 8 -> game complete)
extern volatile uint8_t game_over;
extern volatile uint8_t game_over_timer;

// --- Map Data ---
#define MAP_SIZE 7        // initial maze size (level 1); must be odd
#define MAX_MAP_SIZE 21   // hard cap for maze growth (odd); array bound. Reached at level 8.
// The generated maze: 0 = Wall, 1 = Floor, 2 = Victory Tile (hatch)
extern uint8_t map_size;  // current maze side length (MAP_SIZE + 2*(level-1), capped)
extern uint8_t maze[MAX_MAP_SIZE][MAX_MAP_SIZE];

// --- Fog of War ---
extern uint8_t fog_radius; // Chebyshev visibility radius (2 normally, 1 from level 7)

// --- Camera & Rendering ---
extern uint8_t map_buffer[32 * 32];
extern uint8_t scroll_x;
extern int8_t scroll_y;

extern uint8_t stairs_lx;
extern uint8_t stairs_ly;

// --- Player ---
extern uint8_t player_lx;
extern uint8_t player_ly;
extern uint8_t player_dir; // 0=DR, 1=DL, 2=UL, 3=UR

// --- Movement & Physics State ---
extern uint8_t is_moving;
extern uint8_t is_jumping;
extern uint8_t is_running; // B+direction: 8-frame step, 10 stamina/tile
extern uint8_t move_progress; // 0 to 16
extern int8_t start_lx, start_ly;
extern int8_t target_lx, target_ly;
extern int16_t start_px, start_py;
extern int16_t target_px, target_py;

// --- Stamina System ---
extern uint8_t stamina;
extern uint8_t stamina_recharge_timer;
extern uint8_t stamina_recharge_rate; // frames per +1 stamina (grows with level)

// --- Level Progression ---
extern uint8_t level; // starts at 1; game completes after clearing level 8

// --- Enemy System (multi-entity: up to MAX_ENEMIES ghosts) ---
#define MAX_ENEMIES 8
extern uint8_t num_enemies; // current ghost count (= level, capped at MAX_ENEMIES)
extern uint8_t enemy_step_cooldown; // base pause (frames) between ghost steps; shrinks with level
extern uint8_t enemy_lx[MAX_ENEMIES];
extern uint8_t enemy_ly[MAX_ENEMIES];
extern uint8_t enemy_is_moving[MAX_ENEMIES];
extern uint8_t enemy_move_progress[MAX_ENEMIES];
extern int8_t enemy_start_lx[MAX_ENEMIES], enemy_start_ly[MAX_ENEMIES];
extern int8_t enemy_target_lx[MAX_ENEMIES], enemy_target_ly[MAX_ENEMIES];
extern int16_t enemy_start_px[MAX_ENEMIES], enemy_start_py[MAX_ENEMIES];
extern int16_t enemy_target_px[MAX_ENEMIES], enemy_target_py[MAX_ENEMIES];
extern uint8_t enemy_cooldown[MAX_ENEMIES];

#endif