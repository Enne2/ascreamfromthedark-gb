#ifndef PLAYER_LOGIC_H
#define PLAYER_LOGIC_H

#include <stdint.h>

/**
 * ==========================================
 * PLAYER CONTROLLER LOGIC
 * ==========================================
 * Handles user input, delayed auto-shift (DAS) for movement repeat,
 * and the logic for walking, jumping, and collision.
 */

// Call every frame during gameplay
void update_player_movement(uint8_t keys, uint8_t prev_keys);

#endif
