#include "render.h"
#include "globals.h"
#include <gb/gb.h>
#include <string.h>
#include "tiles.h"
#include "player.h"
#include "enemy.h"
#include "gameover.h"
#include "stamina.h"
#include "level.h"
#include "maze.h"

uint8_t get_tile_state(int8_t cx, int8_t cy, int8_t lx, int8_t ly) {
    if (lx < 0 || (uint8_t)lx >= map_size || ly < 0 || (uint8_t)ly >= map_size) return 0;
    if (maze[ly][lx] == 0) return 0;
    int8_t dx = lx - cx;
    int8_t dy = ly - cy;
    if (dx < 0) dx = -dx;
    if (dy < 0) dy = -dy;
    int8_t dist = (dx > dy) ? dx : dy;
    if (dist > (int8_t)fog_radius) return 0;
    if (dist == (int8_t)fog_radius) return 2;
    return 1;
}

/**
 * Aggiorna l'interfaccia utente (UI) della barra della stamina.
 *
 * Sviluppo & Scelte Architetturali:
 * 1. La UI su Game Boy può essere fatta in Background (HUD window) o tramite Sprite. 
 *    Abbiamo scelto gli Sprite (ID da 18 a 22) perché la Window è più difficile da 
 *    gestire insieme allo scrolling isometrico fluido.
 * 2. Gli sprite sono posizionati a coordinate fisiche fisse sullo schermo 
 *    (es. 112, 16 per l'angolo in alto a destra). Il move_bkg della telecamera NON li muove!
 * 3. La barra è lunga 5 segmenti (40 pixel totali). L'algoritmo converte il valore `stamina` (0-100)
 *    in pixel (0-40) e seleziona il tile giusto dal set per mostrare il bordo arrotondato e
 *    il livello di riempimento.
 */
void update_stamina_display(void) {
    if (game_over) {
        // Nasconde la barra spostando gli sprite fuori schermo quando finisce la partita
        for (uint8_t i = 0; i < 5; i++) {
            move_sprite(18 + i, 0, 0);
        }
        return;
    }
    
    // Posizionamento in alto a destra (+8, +16 sono gli offset hardware del Game Boy per gli sprite)
    move_sprite(18, (uint8_t)(112 + 8), 16);
    move_sprite(19, (uint8_t)(120 + 8), 16);
    move_sprite(20, (uint8_t)(128 + 8), 16);
    move_sprite(21, (uint8_t)(136 + 8), 16);
    move_sprite(22, (uint8_t)(144 + 8), 16);
    
    // Convertiamo 0-100% in 0-40 pixels
    uint16_t temp = (uint16_t)stamina * 40;
    uint8_t num_pixels = temp / 100;
    
    // Offset di base nella VRAM dove sono caricati i tile della stamina
    // Caricato a partire da tiles_TILE_COUNT per non sovrascrivere la VRAM condivisa (>=128)
    uint8_t base_tile = tiles_TILE_COUNT;
    
    for (uint8_t i = 0; i < 5; i++) {
        uint8_t tile_idx;
        if (i == 0) {
            tile_idx = (num_pixels >= 8) ? 11 : 9; // Tappo sinistro pieno (11) o vuoto (9)
        } else if (i == 4) {
            tile_idx = (num_pixels >= 40) ? 12 : 10; // Tappo destro pieno (12) o vuoto (10)
        } else {
            int8_t seg_px = (int8_t)num_pixels - (i * 8);
            if (seg_px < 0) seg_px = 0;
            if (seg_px > 8) seg_px = 8;
            tile_idx = seg_px; // Segmenti centrali (0..8 px)
        }
        
        // Imposta il frame dell'animazione
        set_sprite_tile(18 + i, base_tile + tile_idx * 2);
    }
}

/**
 * Aggiorna l'indicatore del livello (HUD in alto a sinistra).
 *
 * Sviluppo & Scelte Architetturali:
 * 1. Come la barra stamina, usiamo sprite hardware (ID 23..25) perche' il background
 *    e' scrollato isometricamente e non e' adatto a un HUD fisso. Gli sprite sono
 *    coordinate-schermo fisse, indipendenti dallo scroll.
 * 2. L'asset `level.png` contiene 12 glifi 8x16 (blank, 'L', '0'..'9'), caricati in
 *    VRAM sprite subito dopo i tile della stamina (base = tiles_TILE_COUNT +
 *    stamina_TILE_COUNT) per evitare sovrapposizioni con i tile del background
 *    (stesso workaround del commit 93deb35 per la VRAM condivisa).
 * 3. Si mostrano 3 sprite: 'L', decine (blank se livello < 10), unita'.
 *    Viene nascosto durante il game over (sconfitta/vittoria) e sul titolo.
 */
#define LEVEL_HUD_SPRITE   23   // primo OAM ID del livello (dopo stamina 18..22)

void update_level_display(void) {
    // Nascondi durante il game over (sconfitta o vittoria/Going Deeper).
    if (game_over) {
        for (uint8_t i = 0; i < 3; i++) {
            move_sprite(LEVEL_HUD_SPRITE + i, 0, 0);
        }
        return;
    }

    uint8_t base = LEVEL_SPRITE_BASE;
    uint8_t tens = (level / 10) % 10;
    uint8_t ones = level % 10;

    // Mappatura glifi in level.png (11 glifi, ognuno 8x16 = 2 tile, in ordine grazie
    // a -keep_duplicate_tiles). Indice di ordine i -> tile (base + 2*i):
    //   0 = 'L', 1..10 = '0'..'9'. Quindi la cifra d -> indice (1+d) -> tile base + (1+d)*2.
    set_sprite_tile(LEVEL_HUD_SPRITE + 0, base + 0 * 2);                 // 'L' (ordine 0)
    set_sprite_tile(LEVEL_HUD_SPRITE + 2, base + (1 + ones) * 2);         // unita' (cifra ones)

    // Posizionamento in alto a sinistra (offset hardware +8 x, +16 y).
    move_sprite(LEVEL_HUD_SPRITE + 0, 8, 16);    // 'L' a screen x=0
    move_sprite(LEVEL_HUD_SPRITE + 2, 24, 16);    // unita' a screen x=16

    // Decine: mostrate solo se livello >= 10 (altrimenti sprite nascosto offscreen).
    if (level >= 10) {
        set_sprite_tile(LEVEL_HUD_SPRITE + 1, base + (1 + tens) * 2);    // decine (cifra tens)
        move_sprite(LEVEL_HUD_SPRITE + 1, 16, 16);  // screen x=8
    } else {
        move_sprite(LEVEL_HUD_SPRITE + 1, 0, 0);    // nascondi decine
    }
}

/**
 * Disegna la porzione visibile del labirinto e applica il sistema "Fog of War".
 *
 * Sviluppo & Scelte Architetturali:
 * 1. Proiezione Isometrica: Convertiamo le coordinate logiche della griglia X,Y 
 *    in coordinate schermo isometriche. La formula matematica standard è:
 *    iso_x = (X - Y) * (TileWidth / 2)
 *    iso_y = (X + Y) * (TileHeight / 2)
 *    Questo fa ruotare la mappa di 45 gradi e la schiaccia orizzontalmente.
 * 2. Distanza di Chebyshev: Usata per la nebbia. Nascondiamo tutti i blocchi che 
 *    distano logicamente più di 2 caselle dal centro (`max(|dx|, |dy|)`). 
 *    Questo crea un quadrato perfetto di visibilità (5x5) attorno al giocatore,
 *    più leggero da calcolare sul Game Boy rispetto all'Euclidea (che usa la radice quadrata).
 * 3. Auto-Tiling Mask: Calcoliamo dinamicamente quali muri sono adiacenti alla cella
 *    per disegnare bordi e variazioni grafiche (usando bit masking `(has_tl ? 1 : 0) | ...`).
 */
void draw_map(uint8_t center_x, uint8_t center_y) {
    // Svuotiamo l'intero buffer della mappa con l'indice 0 (casella nera vuota)
    memset(map_buffer, 0, sizeof(map_buffer));
    
    // Calcoliamo la "finestra" di mappa (2r+1 x 2r+1) da processare (fog_radius)
    int8_t start_x = center_x - fog_radius;
    if (start_x < 0) start_x = 0;
    int8_t end_x = center_x + fog_radius;
    if ((uint8_t)end_x >= map_size) end_x = map_size - 1;
    
    int8_t start_y = center_y - fog_radius;
    if (start_y < 0) start_y = 0;
    int8_t end_y = center_y + fog_radius;
    if ((uint8_t)end_y >= map_size) end_y = map_size - 1;
    
    // Processiamo la mappa in DUE passate per risolvere il problema dell'overlapping isometrico.
    // L'engine disegna da Nord a Sud. I tile a Sud sovrascrivono la metà inferiore dei tile a Nord.
    // Se disegnassimo le scale nella prima passata, i pavimenti davanti ad esse sovrascriverebbero
    // i gradini con i loro angoli trasparenti (che sono di colore piatto).
    // Disegnandole per ultime, le scale sovrascriveranno i pavimenti davanti, e grazie alle maschere
    // dei propri angoli inferiori, si fonderanno perfettamente con il colore del pavimento.

    // Passata 1: Pavimenti normali
    for (int8_t ly = start_y; ly <= end_y; ly++) {
        for (int8_t lx = start_x; lx <= end_x; lx++) {
            if (maze[ly][lx] == 1) {
                // Distanza di Chebyshev dal giocatore
                int8_t dx = lx - center_x;
                int8_t dy = ly - center_y;
                if (dx < 0) dx = -dx;
                if (dy < 0) dy = -dy;
                int8_t dist = (dx > dy) ? dx : dy;

                if (dist > (int8_t)fog_radius) continue;

                int8_t iso_x = (lx - ly) * 2 + 12;
                int8_t iso_y = (lx + ly) * 1 + 2;
                uint8_t is_alt = ((lx + ly) % 2 == 0);

                uint8_t state_tl = get_tile_state(center_x, center_y, lx - 1, ly);
                uint8_t state_tr = get_tile_state(center_x, center_y, lx, ly - 1);
                uint8_t mask = state_tl + state_tr * 3;

                uint8_t v;
                if (dist == (int8_t)fog_radius) {
                    v = is_alt ? (27 + mask) : (18 + mask);
                } else {
                    v = is_alt ? (9 + mask) : mask;
                }

                for (uint8_t y = 0; y < 2; y++) {
                    for (uint8_t x = 0; x < 4; x++) {
                        uint8_t target_x = (iso_x + x) & 31;
                        uint8_t target_y = (iso_y + y) & 31;
                        uint8_t src_tile = tiles_map[4 + v * 8 + y * 4 + x];
                        map_buffer[target_y * 32 + target_x] = src_tile;
                    }
                }
            }
        }
    }

    // Passata 2: Scala della Vittoria (disegnata sempre sopra)
    for (int8_t ly = start_y; ly <= end_y; ly++) {
        for (int8_t lx = start_x; lx <= end_x; lx++) {
            if (maze[ly][lx] == 2) {
                int8_t dx = lx - center_x;
                int8_t dy = ly - center_y;
                if (dx < 0) dx = -dx;
                if (dy < 0) dy = -dy;
                int8_t dist = (dx > dy) ? dx : dy;

                if (dist > (int8_t)fog_radius) continue;

                int8_t iso_x = (lx - ly) * 2 + 12;
                int8_t iso_y = (lx + ly) * 1 + 2;
                uint8_t is_alt = ((lx + ly) % 2 == 0);

                uint8_t state_tl = get_tile_state(center_x, center_y, lx - 1, ly);
                uint8_t state_tr = get_tile_state(center_x, center_y, lx, ly - 1);
                uint8_t state_bl = get_tile_state(center_x, center_y, lx, ly + 1);
                uint8_t state_br = get_tile_state(center_x, center_y, lx + 1, ly);
                
                uint16_t mask = state_tl + state_tr * 3 + state_bl * 9 + state_br * 27;

                uint16_t v;
                if (dist == (int8_t)fog_radius) {
                    v = is_alt ? (36 + 243 + mask) : (36 + 162 + mask);
                } else {
                    v = is_alt ? (36 + 81 + mask) : (36 + mask);
                }

                for (uint8_t y = 0; y < 2; y++) {
                    for (uint8_t x = 0; x < 4; x++) {
                        uint8_t target_x = (iso_x + x) & 31;
                        uint8_t target_y = (iso_y + y) & 31;
                        uint8_t src_tile = tiles_map[4 + v * 8 + y * 4 + x];
                        map_buffer[target_y * 32 + target_x] = src_tile;
                    }
                }
            }
        }
    }
    
    update_stamina_display();
    
    // Flush dinamico a 16 righe (512 byte) centrato sulla iso_y del centro di disegno,
    // con gestione del wrap della mappa 32x32. 16 righe = prestazioni del progetto
    // originale; centrando su center_iso_y la nebbia ricade sempre nelle righe flussate
    // anche nei labirinti grandi, dove le iso_y assolute wrappano fuori dal vecchio
    // range fisso 2-17.
    int16_t center_iso_y = (int16_t)center_x + (int16_t)center_y + 2;
    uint8_t start = (uint8_t)((center_iso_y - 8) & 31);
    if (start + 16 <= 32) {
        set_bkg_tiles(0, start, 32, 16, &map_buffer[(uint16_t)start * 32]);
    } else {
        uint8_t first = 32 - start;
        set_bkg_tiles(0, start, 32, first, &map_buffer[(uint16_t)start * 32]);
        set_bkg_tiles(0, 0, 32, 16 - first, map_buffer);
    }
}

/**
 * Aggiorna il registro scroll hardware della telecamera (SCX, SCY)
 * calcolando la proiezione isometrica in pixel e centrandola nello schermo (160/2, 144/2).
 */
void update_camera(void) {
    // Coordinate fisiche pixel calcolate allo stesso modo del motore grafico
    int16_t px = (player_lx - player_ly) * 16 + 96; 
    int16_t py = (player_lx + player_ly) * 8 + 16;   
    
    // Centra il pixel px,py in mezzo allo schermo (-64 e -72)
    scroll_x = px - 64;
    scroll_y = py - 72;
    
    // Comando hardware GBDK per scrollare il livello Background
    move_bkg(scroll_x, scroll_y);
}

/**
 * Aggiorna il metasprite 16x16 del giocatore.
 * Applica l'animazione di camminata o l'arco parabolico per l'altezza del salto.
 */
void update_player_sprite(void) {
    // Animazione di camminata (alterna tra due frame a seconda del `move_progress`)
    uint8_t frame_offset = is_moving ? ((move_progress >> 2) & 1) : 0;
    
    uint8_t y_offset = 0;
    if (is_jumping) {
        // Matematica dell'Arco Parabolico per il salto.
        // x * (16 - x) crea una curva che sale a 16 px di apice a metà altezza (8 frame).
        y_offset = (move_progress * (16 - move_progress)) >> 2;
    }
    
    // Animazione discesa botola: il giocatore scende di pochi pixel
    if (descend_offset > 0) {
        y_offset = (uint8_t)(-(int8_t)(descend_offset >> 1)); // discesa graduale
    }
    
    // move_metasprite e' fornito da png2asset e posiziona multipli sprite hardware insieme
    // Il giocatore e' sempre fisso al centro dello schermo (88, 88). E' il mondo (sfondo) a muoversi.
    move_metasprite(player_metasprites[player_dir * 2 + frame_offset], 0, 0, 88, 88 - y_offset);
}
