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

// Main loop sequencer: drives the finale music directly, bypassing play_music_tick
// (which would otherwise play the gameplay track or other branches).
static uint8_t finale_step = 0;
static uint8_t finale_timer = 0;
#define FINALE_PERIOD 14  // frames per note (~4 notes/sec)

static void drive_finale(void) {
    finale_timer++;
    if (finale_timer >= FINALE_PERIOD) {
        finale_timer = 0;
        play_finale_step(finale_step);
        finale_step++;
        if (finale_step >= 192) {
            finale_step = 0; // loop
        }
    }
}

void main(void) {
    SPRITES_8x16;

    OBP0_REG = 0xE4;
    OBP1_REG = 0x1B;
    BGP_REG = 0x1B;

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

    // Init audio for the finale
    NR52_REG = 0x80;
    NR50_REG = 0x77;
    NR51_REG = 0xFF;
    // Do NOT register play_music_tick as VBL — we drive the finale from main loop.
    remove_VBL(play_music_tick);

    SHOW_BKG;
    SHOW_SPRITES;
    DISPLAY_ON;

    uint8_t prev_keys = 0;
    while (1) {
        wait_vbl_done();
        drive_finale();
        uint8_t keys = joypad();
        if ((keys & J_START) && !(prev_keys & J_START)) {
            level = 1;
            break;
        }
        prev_keys = keys;
    }
}