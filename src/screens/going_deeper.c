#include "screens.h"
#include "../globals.h"
#include <string.h>

// Schermata di transizione livello (game_over == 2: Going Deeper)
void show_going_deeper(void) {
    HIDE_SPRITES;
    SCX_REG = 0;
    SCY_REG = 0;
    font_init();
    font_t gd_font = font_load(font_ibm);
    font_set(gd_font);
    memset(map_buffer, 0, sizeof(map_buffer));
    ending_puttext(2, 7,  "GOING DEEPER");
    ending_puttext(3, 9,  "LEVEL");
    ending_putdigit(9, 9, (uint8_t)(level + 1));
    set_bkg_tiles(0, 0, 32, 32, map_buffer);
}