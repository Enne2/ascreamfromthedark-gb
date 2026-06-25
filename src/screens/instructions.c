#include "screens.h"
#include "../globals.h"
#include <string.h>

// Schermata istruzioni (livello 1 / SELECT). Usa il Window layer:
// il BG map del gameplay resta intatto -> niente garbage alla chiusura.
void show_instructions(void) {
    HIDE_SPRITES;
    font_init();
    font_t hint_font = font_load(font_ibm);
    font_set(hint_font);
    BGP_REG = 0x1B; // palette invertita (sfondo nero, testo chiaro)
    memset(map_buffer, 0, sizeof(map_buffer));

    ending_puttext(3, 2, "FIND THE HATCH");
    ending_puttext(4, 8, "DPAD WALK");
    ending_puttext(2, 9, "A + DPAD JUMP");
    ending_puttext(2, 10, "B + DPAD RUN");
    ending_puttext(2, 12, "PRESS B");
    ending_puttext(2, 13, "TO CONTINUE");
    // Window layer: tile map separato (0x9C00) dal BG (0x9800)
    set_win_tiles(0, 0, 32, 32, map_buffer);
    move_win(7, 0); // -7 pixel offset: allinea a sinistra
    SHOW_WIN;
}