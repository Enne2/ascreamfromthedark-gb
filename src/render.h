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

// Invalidate the cached VRAM bounds before entering a newly initialized level.
void reset_map_render_cache(void);

// Update the background camera scroll position to center the player
void update_camera(void);

// Update stamina bar graphics
void update_stamina_display(void);

// Update the level indicator (top-left HUD)
void update_level_display(void);

// In 8x16 mode the hardware ignores the tile-index LSB. Both sprite asset
// blocks therefore start at an even tile and occupy their real generated size.
#define STAMINA_SPRITE_BASE ((uint8_t)((tiles_TILE_COUNT + 1u) & (uint8_t)0xFEu))
#define LEVEL_SPRITE_BASE   ((uint8_t)((STAMINA_SPRITE_BASE + stamina_TILE_COUNT + 1u) & (uint8_t)0xFEu))

// Update the player sprite (animation frames, jumping height offset)
void update_player_sprite(void);

#endif
