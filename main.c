#include <gb/gb.h>
#include "engine.h"

void main(void) {
    engine_init();
    
    SHOW_BKG;
    SHOW_SPRITES;
    DISPLAY_ON;
    
    uint8_t prev_keys = 0;
    
    while (1) {
        wait_vbl_done();
        uint8_t keys = joypad();
        engine_update(keys, prev_keys);
        prev_keys = keys;
    }
}
