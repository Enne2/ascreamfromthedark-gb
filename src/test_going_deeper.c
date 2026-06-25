#include <gb/gb.h>
#include <gbdk/font.h>
#include "globals.h"
#include "screens/screens.h"

void main(void) {
    SPRITES_8x16;
    SHOW_BKG;
    SHOW_WIN;
    DISPLAY_ON;
    level = 3;
    game_over = 2;
    game_over_timer = 0;
    show_going_deeper();
    while(1) wait_vbl_done();
}
