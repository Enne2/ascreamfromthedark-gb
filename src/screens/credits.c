#include "screens.h"
#include "../globals.h"
#include <string.h>

// Schermata dei crediti (SELECT nel menu titolo). Usa il Window layer.
// Il BG map del titolo resta intatto -> tornando al titolo niente garbage.
void show_credits(void) {
    HIDE_SPRITES;
    font_init();
    font_t cr_font = font_load(font_ibm);
    font_set(cr_font);
    BGP_REG = 0x1B; // palette invertita (sfondo nero, testo chiaro)
    memset(map_buffer, 0, sizeof(map_buffer));
    ending_puttext(3, 1,  "A SCREAM FROM");
    ending_puttext(6, 2,  "THE DARK");
    ending_puttext(2, 5,  "A GAME BY");
    ending_puttext(3, 6,  "MATTEO B.");
    ending_puttext(2, 9,  "GBDK 2020");
    ending_puttext(2, 10, "SDCC SM83");
    ending_puttext(2, 11, "PYBOY TEST");
    ending_puttext(1, 14, "PRESS B TO RETURN");
    // Window layer: tile map separato dal BG
    set_win_tiles(0, 0, 32, 32, map_buffer);
    move_win(7, 0);
    SHOW_WIN;
}