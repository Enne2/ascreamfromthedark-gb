#include <gb/gb.h>
#include "engine.h"
#include "globals.h"
#include "screens/screens.h"
#include "title_bg.h"

uint8_t app_state = 0; // 0 = title, 1 = game

void main(void) {
    title_init();

    SHOW_BKG;
    SHOW_SPRITES;
    DISPLAY_ON;

    uint8_t prev_keys = 0;

    while (1) {
        wait_vbl_done();
        uint8_t keys = joypad();

        if (app_state == 0) {
            if (credits_active) {
                // Credits: B per tornare al titolo
                if ((keys & J_B) && !(prev_keys & J_B)) {
                    HIDE_WIN;
                    BGP_REG = 0xE4;
                    set_bkg_data(0, title_bg_TILE_COUNT, title_bg_tiles);
                    set_bkg_tiles(0, 0, title_bg_WIDTH / 8, title_bg_HEIGHT / 8, title_bg_map);
                    credits_active = 0;
                }
            } else if (intro_active) {
                // Intro: un tasto qualsiasi avvia la partita
                if (keys && !prev_keys) {
                    HIDE_WIN;
                    BGP_REG = 0xE4;
                    app_state = 1;
                    level = 1;
                    intro_active = 0;
                    engine_init();
                }
            } else {
                title_update(keys, prev_keys);
                // START: mostra l'introduzione alla storia
                if ((keys & J_START) && !(prev_keys & J_START)) {
                    intro_active = 1;
                    show_intro();
                }
                // SELECT: mostra i crediti
                if ((keys & J_SELECT) && !(prev_keys & J_SELECT)) {
                    show_credits();
                    credits_active = 1;
                }
            }
        } else {
            engine_update(keys, prev_keys);
        }

        prev_keys = keys;
    }
}