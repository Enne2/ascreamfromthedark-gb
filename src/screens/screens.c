#include "screens.h"
#include "../globals.h"
#include <string.h>

/**
 * Helper condivisi per scrivere testo nel map_buffer usando gli indici
 * tile del font IBM (tile = ASCII - 32, il font parte dallo spazio).
 */

void ending_puttext(uint8_t col, uint8_t row, const char *s) {
    uint8_t i = 0;
    while (s[i]) {
        if (col + i < 32) {
            map_buffer[(uint16_t)row * 32 + col + i] = (uint8_t)(s[i] - ' ');
        }
        i++;
    }
}

void ending_putdigit(uint8_t col, uint8_t row, uint8_t digit) {
    if (col < 32) {
        map_buffer[(uint16_t)row * 32 + col] = (uint8_t)(digit + ('0' - ' '));
    }
}