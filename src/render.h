#ifndef RENDER_H
#define RENDER_H

#include <stdint.h>

/**
 * ==========================================
 * RENDERING & CAMERA SUBSYSTEM
 * ==========================================
 * Handles updating visual elements on the screen, including the map background,
 * stamina bar interface, and the player sprite.
 */

// Draw the isometric map centered around a specific logical tile
void draw_map(uint8_t center_x, uint8_t center_y);

// Update the background camera scroll position to center the player
void update_camera(void);

// Update stamina bar graphics
void update_stamina_display(void);

// Update the player sprite (animation frames, jumping height offset)
void update_player_sprite(void);

#endif
