#include "screens.h"
#include "../globals.h"
#include <string.h>

// Schermata di introduzione alla storia (dopo START, prima del gioco).
// Si chiude con un tasto qualsiasi. Usa il Window layer.
void show_intro(void) {
    HIDE_SPRITES;
    font_init();
    font_t intro_font = font_load(font_ibm);
    font_set(intro_font);
    BGP_REG = 0x1B;
    memset(map_buffer, 0, sizeof(map_buffer));
    ending_puttext(2, 1,  "You were walking");
    ending_puttext(1, 2,  "alone in the dead");
    ending_puttext(6, 3,  "of night.");
    ending_puttext(1, 5,  "Without warning, an");
    ending_puttext(1, 6,  "unnatural darkness");
    ending_puttext(0, 7,  "consumed the world.");
    ending_puttext(1, 9,  "Your only comfort:");
    ending_puttext(3, 10, "a faint torch.");
    ending_puttext(0, 12, "The path behind you");
    ending_puttext(6, 13, "is gone.");
    ending_puttext(0, 15, "Descend deeper into");
    ending_puttext(6, 16, "the unknown.");
    set_win_tiles(0, 0, 32, 32, map_buffer);
    move_win(7, 0);
    SHOW_WIN;
}