#include <gb/gb.h>
#include "engine.h"
#include "globals.h"

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
            title_update(keys, prev_keys);
            if ((keys & J_START) && !(prev_keys & J_START)) {
                app_state = 1;
                level = 1; // Nuova partita dal livello 1
                engine_init();
            }
        } else {
            engine_update(keys, prev_keys);
        }
        
        prev_keys = keys;
    }
}
