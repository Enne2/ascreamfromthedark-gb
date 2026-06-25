#include "screens.h"
#include "../globals.h"
#include <string.h>

// Schermata del finale tragico (game_over == 3: la torcia si e' spenta).
// SPOILER: il testo e' in questo file (non nella documentazione).
void show_finale(void) {
    HIDE_SPRITES;
    SCX_REG = 0;
    SCY_REG = 0;
    BGP_REG = 0x1B; // palette invertita: sfondo nero, testo chiaro
    font_init();
    font_t end_font = font_load(font_ibm);
    font_set(end_font);
    memset(map_buffer, 0, sizeof(map_buffer));
    ending_puttext(3, 4,  "YOUR TORCH HAS");
    ending_puttext(6, 5,  "RUN OUT,");
    ending_puttext(2, 7,  "YOU ARE TRAPPED.");
    ending_puttext(0, 10, "JUST ANOTHER SCREAM");
    ending_puttext(3, 11, "FROM THE DARK.");
    ending_puttext(5, 14, "GAME OVER");
    set_bkg_tiles(0, 0, 32, 32, map_buffer);
}