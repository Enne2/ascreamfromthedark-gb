#ifndef GLOBALS_H
#define GLOBALS_H

#include <stdint.h>

/**
 * ==========================================
 * GLOBAL GAME STATE
 * ==========================================
 * This file contains all the global variables that are shared across different
 * logical modules (e.g., rendering, player logic, enemy logic, audio).
 * We place them here to avoid circular dependencies between modules.
 */

// --- General Application State ---
// app_state = 0 means Title Screen, 1 means Gameplay
extern uint8_t app_state;

// game_over = 0 means Playing, 1 means Defeat (Ghost caught you), 2 means Victory (Reached portal)
extern volatile uint8_t game_over;
// Timer used to delay actions after game over (e.g. before showing text or playing music)
extern volatile uint8_t game_over_timer;

// --- Map Data ---
#define MAP_SIZE 7
// The generated maze: 0 = Wall, 1 = Floor, 2 = Victory Tile
extern uint8_t maze[MAP_SIZE][MAP_SIZE];

// --- Camera & Rendering ---
// Map buffer used to draw the isometric tiles into the Game Boy Background map
extern uint8_t map_buffer[32 * 32];
// Camera scroll coordinates to keep the player centered
extern uint8_t scroll_x;
extern int8_t scroll_y;

extern uint8_t stairs_lx;
extern uint8_t stairs_ly;

// --- Mappa e Entità ---
// The generated maze: 0 = Wall, 1 = Floor, 2 = Victory Tile
extern uint8_t maze[MAP_SIZE][MAP_SIZE];
extern uint8_t player_lx;
extern uint8_t player_ly;
extern uint8_t player_dir; // 0=DR, 1=DL, 2=UL, 3=UR

// --- Movement & Physics State ---
// Shared variables for interpolated movement (walking/jumping)
extern uint8_t is_moving;
extern uint8_t is_jumping;
extern uint8_t is_running; // B+direction: step in 8 frames instead of 16, costs 10 stamina/tile
extern uint8_t move_progress; // 0 to 16, tracks the sub-tile animation progress
extern int8_t start_lx, start_ly;
extern int8_t target_lx, target_ly;
extern int16_t start_px, start_py;
extern int16_t target_px, target_py;

// --- Stamina System ---
// Stamina powers the jump/run mechanic. 100 = full. Recharges over time.
extern uint8_t stamina;
extern uint8_t stamina_recharge_timer;

// --- Level Progression ---
// Current level (starts at 1, increments each time the hatch is reached).
extern uint8_t level;

// --- Enemy State ---
extern uint8_t enemy_lx;
extern uint8_t enemy_ly;
extern uint8_t enemy_is_moving;
extern uint8_t enemy_move_progress;
extern int8_t enemy_start_lx, enemy_start_ly;
extern int8_t enemy_target_lx, enemy_target_ly;
extern int16_t enemy_start_px, enemy_start_py;
extern int16_t enemy_target_px, enemy_target_py;
extern uint8_t enemy_cooldown;

#endif
