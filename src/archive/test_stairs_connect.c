#include <gb/gb.h>
#include <gbdk/font.h>
#include <stdint.h>
#include <string.h>

#include "tiles.h"

// Buffer di 32x32 tiles (mappa hardware del Game Boy)
uint8_t bkg_buffer[1024];

void main(void) {
    // Inizializza il Game Boy
    DISPLAY_OFF;

    // Carica il tileset in VRAM
    set_bkg_data(0, tiles_TILE_COUNT, tiles_tiles);

    memset(bkg_buffer, 0, sizeof(bkg_buffer));

    // Disegniamo una griglia 3x3
    // La griglia e formata da blocchi 4x2 hardware tiles
    // Il blocco centrale sara le scale (variante 64), il resto pavimenti normali (variante 16)
    
    // Per avere maschere corrette (nessun bordo nero tra di loro):
    // La griglia 3x3 sara:
    // (0,0), (1,0), (2,0)
    // (0,1), (1,1), (2,1)
    // (0,2), (1,2), (2,2)
    
    for (int8_t ly = 0; ly < 3; ly++) {
        for (int8_t lx = 0; lx < 3; lx++) {
            
            // Coordinate isometriche
            int8_t iso_x = (lx - ly) * 2 + 12; 
            int8_t iso_y = (lx + ly) * 1 + 6;  // Spostato giu per centrarlo

            uint8_t has_tl = (lx > 0);
            uint8_t has_tr = (ly > 0);
            uint8_t has_bl = (ly < 2);
            uint8_t has_br = (lx < 2);
            uint8_t mask = (has_tl ? 1 : 0) | (has_tr ? 2 : 0) | (has_bl ? 4 : 0) | (has_br ? 8 : 0);

            uint8_t is_alt = ((lx + ly) % 2 == 0);
            
            uint8_t v;
            if (lx == 1 && ly == 1) {
                // Scale (centro)
                v = 64 + mask;
            } else {
                // Pavimento normale
                v = is_alt ? (16 + mask) : mask;
            }

            for (uint8_t y = 0; y < 2; y++) {
                for (uint8_t x = 0; x < 4; x++) {
                    uint8_t target_x = (iso_x + x) & 31;
                    uint8_t target_y = (iso_y + y) & 31;
                    
                    uint8_t src_tile = tiles_map[4 + v * 8 + y * 4 + x];
                    bkg_buffer[target_y * 32 + target_x] = src_tile;
                }
            }
        }
    }

    set_bkg_tiles(0, 0, 32, 32, bkg_buffer);

    SHOW_BKG;
    DISPLAY_ON;

    while(1) {
        wait_vbl_done();
    }
}
