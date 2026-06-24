#include "globals.h"

// Define the actual memory storage for all global variables
volatile uint8_t game_over = 0;
volatile uint8_t game_over_timer = 0;

uint8_t map_size = MAP_SIZE;
uint8_t maze[MAX_MAP_SIZE][MAX_MAP_SIZE];
uint8_t map_buffer[32 * 32];

uint8_t fog_radius = 2;

uint8_t player_lx = 1;
uint8_t player_ly = 1;
uint8_t player_dir = 0;
uint8_t scroll_x = 0;
int8_t scroll_y = 0;

uint8_t stairs_lx = 0;
uint8_t stairs_ly = 0;

uint8_t is_moving = 0;
uint8_t is_jumping = 0;
uint8_t is_running = 0;
uint8_t move_progress = 0;
int8_t start_lx, start_ly;
int8_t target_lx, target_ly;
int16_t start_px, start_py;
int16_t target_px, target_py;

uint8_t stamina = 100;
uint8_t stamina_recharge_timer = 0;
uint8_t stamina_recharge_rate = 60;

uint8_t level = 1;

uint8_t num_enemies = 1;
uint8_t enemy_step_cooldown = 60;
uint8_t enemy_lx[MAX_ENEMIES] = {0};
uint8_t enemy_ly[MAX_ENEMIES] = {0};
uint8_t enemy_is_moving[MAX_ENEMIES] = {0};
uint8_t enemy_move_progress[MAX_ENEMIES] = {0};
int8_t enemy_start_lx[MAX_ENEMIES], enemy_start_ly[MAX_ENEMIES];
int8_t enemy_target_lx[MAX_ENEMIES], enemy_target_ly[MAX_ENEMIES];
int16_t enemy_start_px[MAX_ENEMIES], enemy_start_py[MAX_ENEMIES];
int16_t enemy_target_px[MAX_ENEMIES], enemy_target_py[MAX_ENEMIES];
uint8_t enemy_cooldown[MAX_ENEMIES] = {0};