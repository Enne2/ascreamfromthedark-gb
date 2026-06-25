#include "screens.h"
#include "../globals.h"
#include <string.h>

// Schermata di sconfitta (game_over == 1: il buio ti reclama)
void show_death(void) {
    HIDE_SPRITES;
    SCX_REG = 0;
    SCY_REG = 0;
    BGP_REG = 0x1B; // palette invertita (sfondo nero, testo chiaro)
    font_init();
    font_t dead_font = font_load(font_ibm);
    font_set(dead_font);
    memset(map_buffer, 0, sizeof(map_buffer));
    ending_puttext(5, 3,  "YOU DIED");
    ending_puttext(2, 5,  "THE DARK CLAIMS");
    ending_puttext(5, 6,  "ANOTHER");
    ending_puttext(2, 9,  "JUST ANOTHER SCREAM");
    ending_puttext(3, 10, "FROM THE DARK.");
    ending_puttext(5, 14, "GAME OVER");
    set_bkg_tiles(0, 0, 32, 32, map_buffer);
}