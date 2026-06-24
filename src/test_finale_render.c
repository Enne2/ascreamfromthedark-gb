#include <gb/gb.h>
#include <stdint.h>
#include <string.h>
#include <gbdk/font.h>

#include "globals.h"
#include "sound.h"

uint8_t app_state = 1;  // sound.c references this; not used in this test

static void ending_puttext(uint8_t col, uint8_t row, const char *s) {
    uint8_t i = 0;
    while (s[i]) {
        if (col + i < 32) {
            map_buffer[(uint16_t)row * 32 + col + i] = (uint8_t)(s[i] - ' ');
        }
        i++;
    }
}

void main(void) {
    SPRITES_8x16;

    OBP0_REG = 0xE4;
    OBP1_REG = 0x1B;
    BGP_REG = 0x1B;  // inverted palette: dark bg, light text

    memset(map_buffer, 0, sizeof(map_buffer));
    set_bkg_tiles(0, 0, 32, 32, map_buffer);

    font_init();
    font_t f = font_load(font_ibm);
    font_set(f);

    ending_puttext(3, 4,  "YOUR TORCH HAS");
    ending_puttext(6, 5,  "RUN OUT,");
    ending_puttext(2, 7,  "YOU ARE TRAPPED.");
    ending_puttext(0, 10, "JUST ANOTHER SCREAM");
    ending_puttext(3, 11, "FROM THE DARK.");
    ending_puttext(5, 14, "GAME OVER");
    set_bkg_tiles(0, 0, 32, 32, map_buffer);

    NR52_REG = 0x80;
    NR50_REG = 0x77;
    NR51_REG = 0xFF;
    sound_reset_music_state();
    remove_VBL(play_music_tick);
    add_VBL(play_music_tick);

    // Trigger the finale music sequencer immediately (skip the 30-frame timer
    // that the main game uses; here we want the music from frame 0).
    game_over = 3;
    game_over_timer = 0;

    SHOW_BKG;
    SHOW_SPRITES;
    DISPLAY_ON;

    uint8_t prev_keys = 0;
    while (1) {
        wait_vbl_done();
        uint8_t keys = joypad();
        if ((keys & J_START) && !(prev_keys & J_START)) {
            level = 1;
            break;
        }
        prev_keys = keys;
    }
}