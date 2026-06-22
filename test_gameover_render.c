#include <gb/gb.h>
#include <stdint.h>
#include <string.h>

#include "player.h"
#include "gameover.h"

// Define dummy / simple map buffer to clear the screen
static uint8_t map_buffer[32 * 32];

void main(void) {
    SPRITES_8x16;
    
    // Set standard palettes
    OBP0_REG = 0xE4;
    OBP1_REG = 0x1B;
    BGP_REG = 0xE4;
    
    // Clear background (completely black empty tiles)
    memset(map_buffer, 0, sizeof(map_buffer));
    set_bkg_tiles(0, 0, 32, 32, map_buffer);
    
    // Load player and gameover sprite data
    set_sprite_data(0, player_TILE_COUNT, player_tiles);
    set_sprite_data(player_TILE_COUNT, gameover_TILE_COUNT, gameover_tiles);
    
    // Render player sprite at center screen (88, 88)
    move_metasprite(player_metasprites[0], 0, 0, 88, 88);
    
    // Render gameover metasprite centered horizontally (88, due to sprite X-offset) and below player (120)
    move_metasprite(gameover_metasprites[0], player_TILE_COUNT, 8, 88, 120);
    
    SHOW_SPRITES;
    SHOW_BKG;
    DISPLAY_ON;
    
    // Loop forever
    while (1) {
        wait_vbl_done();
    }
}
