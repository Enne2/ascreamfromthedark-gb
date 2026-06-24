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

// Update the level indicator (top-left HUD)
void update_level_display(void);

// Base VRAM sprite tile index for the level HUD glyphs. Placed after the full stamina
// load claim and aligned UP to an EVEN tile index: in 8x16 sprite mode the hardware
// ignores the tile-index LSB, so the base must be even for base + 2*i to land on the
// glyph's top tile. Disjoint from BG tile block and stamina (same rationale as 93deb35).
#define LEVEL_SPRITE_BASE  ((uint8_t)(((tiles_TILE_COUNT + (uint8_t)(stamina_TILE_COUNT * 2)) + 1) & (uint8_t)0xFEu))

// Update the player sprite (animation frames, jumping height offset)
void update_player_sprite(void);

#endif
