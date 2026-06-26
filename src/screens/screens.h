#ifndef SCREENS_H
#define SCREENS_H

#include <gb/gb.h>
#include <gbdk/font.h>
#include <stdint.h>

/**
 * Schermate testuali (font IBM, palette invertita 0x1B = sfondo nero).
 * Ogni funzione renderizza la propria schermata nel map_buffer e la
 * flusha sulla BG map (o Window per l'hint). Il chiamante gestisce
 * BGP, font_init/font_load, HIDE/SHOW_SPRITES e il ripristino dei tile.
 */

// Schermata del titolo ( chiamata da title_init )

// Schermata istruzioni (livello 1 / SELECT). Usa il Window layer.
void show_instructions(void);

// Schermata di sconfitta (game_over == 1)
void show_death(void);

// Schermata di transizione livello (game_over == 2)
void show_going_deeper(void);

// Schermata del finale tragico (game_over == 3)
void show_finale(void);

// Schermata dei crediti (SELECT nel menu titolo)
void show_credits(void);

// Schermata di introduzione alla storia (dopo START, prima del gioco)
void show_intro(void);

// Helper condivisi (definiti in screens.c)
void ending_puttext(uint8_t col, uint8_t row, const char *s);
void ending_putdigit(uint8_t col, uint8_t row, uint8_t digit);

#endif