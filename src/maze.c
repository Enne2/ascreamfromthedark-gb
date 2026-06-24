#include "maze.h"
#include "globals.h"
#include <string.h>
#include <rand.h>

// Capacita' massima degli array di appoggio (in WRAM, statici per non saturare
// lo stack hardware del LR35902). Le stanze del DFS sono le celle dispari:
// al massimo (MAX_MAP_SIZE/2)^2 = 8*8 = 64 per un labirinto 17x17.
#define MAX_ROOMS ((MAX_MAP_SIZE / 2) * (MAX_MAP_SIZE / 2))
#define MAX_CELLS (MAX_MAP_SIZE * MAX_MAP_SIZE)

// Array di appoggio statici (in WRAM, non sullo stack hardware).
static uint8_t stack_x[MAX_ROOMS];
static uint8_t stack_y[MAX_ROOMS];
static uint8_t valid_x[MAX_CELLS];
static uint8_t valid_y[MAX_CELLS];

/**
 * Generates a randomized maze using a Depth-First Search (DFS) algorithm with backtracking.
 *
 * Sviluppo & Scelte Architetturali:
 * 1. Perché DFS? Garantisce che ogni cella sia raggiungibile dalla partenza (nessuna isola).
 * 2. Il labirinto è una griglia map_size x map_size (cresce col livello, da MAP_SIZE a
 *    MAX_MAP_SIZE) in cui le celle dispari (1,1 o 3,3) sono le stanze e le pari sono i muri
 *    divisori. Il DFS scava i muri saltando di 2 in 2 e abbattendo il muro in mezzo.
 * 3. Fase post-DFS: riapre casualmente il 15% dei muri per creare loop (vitali per
 *    aggirare l'inseguitore).
 * 4. La BOTOLA (traguardo) viene piazzata su una cella a sufficiente distanza (Chebyshev
 *    >= map_size/2) dalla partenza (1,1), in modo che sia sempre lontana ma su qualunque tile.
 */
void generate_maze(void) {
    uint8_t sz = map_size;

    // 1. Inizializziamo l'intera mappa a 0 (Muro / Spazio Vuoto)
    memset(maze, 0, sizeof(maze));

    uint8_t stack_ptr = 0;

    // Partiamo sempre dalle coordinate (1, 1) in alto a sinistra
    uint8_t cx = 1;
    uint8_t cy = 1;
    maze[cy][cx] = 1; // 1 = Pavimento calpestabile

    while (1) {
        // Cerchiamo i vicini non visitati a distanza 2 (saltando il muro divisorio)
        uint8_t nx[4];
        uint8_t ny[4];
        uint8_t count = 0;

        // Su
        if (cy >= 3 && maze[cy - 2][cx] == 0) {
            nx[count] = cx; ny[count] = cy - 2; count++;
        }
        // Giù
        if (cy <= sz - 4 && maze[cy + 2][cx] == 0) {
            nx[count] = cx; ny[count] = cy + 2; count++;
        }
        // Sinistra
        if (cx >= 3 && maze[cy][cx - 2] == 0) {
            nx[count] = cx - 2; ny[count] = cy; count++;
        }
        // Destra
        if (cx <= sz - 4 && maze[cy][cx + 2] == 0) {
            nx[count] = cx + 2; ny[count] = cy; count++;
        }

        // Se ci sono vicini validi
        if (count > 0) {
            // Scegli una direzione a caso tra quelle disponibili
            uint8_t dir = rand() % count;

            // Salviamo la cella corrente nello stack per poterci tornare
            stack_x[stack_ptr] = cx;
            stack_y[stack_ptr] = cy;
            stack_ptr++;

            // Abbattiamo il muro nel mezzo (media aritmetica delle coordinate)
            maze[(cy + ny[dir]) / 2][(cx + nx[dir]) / 2] = 1;

            // Spostiamo la posizione corrente sul vicino scelto
            cx = nx[dir];
            cy = ny[dir];
            maze[cy][cx] = 1;
        }
        // Se non ci sono vicini, torna indietro prendendo l'ultima cella dallo stack
        else if (stack_ptr > 0) {
            stack_ptr--;
            cx = stack_x[stack_ptr];
            cy = stack_y[stack_ptr];
        }
        // Se lo stack è vuoto, abbiamo visitato tutte le celle: il labirinto è completo!
        else {
            break;
        }
    }

    // FASE 2: Riapriamo casualmente dei muri per creare percorsi alternativi e loop (15%).
    // Cruciale per la giocabilità: permette al giocatore di aggirare l'inseguitore!
    for (uint8_t y = 1; y < sz - 1; y++) {
        for (uint8_t x = 1; x < sz - 1; x++) {
            if (maze[y][x] == 0) {
                // Muro che connette orizzontalmente o verticalmente due corridoi
                if ((maze[y][x - 1] == 1 && maze[y][x + 1] == 1) ||
                    (maze[y - 1][x] == 1 && maze[y + 1][x] == 1)) {
                    if ((rand() % 100) < 15) {
                        maze[y][x] = 1;
                    }
                }
            }
        }
    }

    // FASE 3: Posizionamento della Botola (Traguardo).
    // La botola viene piazzata su una cella calpestabile a "sufficiente distanza" (Chebyshev
    // >= map_size/2) dalla partenza (1,1): sempre lontana, ma su una qualunque tile.
    // La soglia scala con la dimensione del labirinto (3 per 7x7, 8 per 17x17).
    uint8_t min_goal = sz / 2;
    if (min_goal < 3) min_goal = 3;
    uint8_t num_valid = 0;

    for (uint8_t y = 1; y < sz - 1; y++) {
        for (uint8_t x = 1; x < sz - 1; x++) {
            if (maze[y][x] == 1) {
                int8_t dx = (int8_t)x - 1;
                int8_t dy = (int8_t)y - 1;
                if (dx < 0) dx = -dx;
                if (dy < 0) dy = -dy;
                int8_t dist = (dx > dy) ? dx : dy;
                if (dist >= (int8_t)min_goal) {
                    valid_x[num_valid] = x;
                    valid_y[num_valid] = y;
                    num_valid++;
                }
            }
        }
    }

    if (num_valid > 0) {
        uint8_t pick = rand() % num_valid;
        uint8_t target_x = valid_x[pick];
        uint8_t target_y = valid_y[pick];
        maze[target_y][target_x] = 2;
        stairs_lx = target_x;
        stairs_ly = target_y;
    } else {
        // Fallback estremo: nessuna cella a sufficienza distante. Sceglie la cella
        // calpestabile piu' lontana in assoluto da (1,1).
        uint8_t best_x = sz - 2;
        uint8_t best_y = sz - 2;
        int8_t best_dist = -1;
        for (uint8_t y = 1; y < sz - 1; y++) {
            for (uint8_t x = 1; x < sz - 1; x++) {
                if (maze[y][x] == 1) {
                    int8_t dx = (int8_t)x - 1;
                    int8_t dy = (int8_t)y - 1;
                    if (dx < 0) dx = -dx;
                    if (dy < 0) dy = -dy;
                    int8_t dist = (dx > dy) ? dx : dy;
                    if (dist > best_dist) {
                        best_dist = dist;
                        best_x = x;
                        best_y = y;
                    }
                }
            }
        }
        maze[best_y][best_x] = 2;
        stairs_lx = best_x;
        stairs_ly = best_y;
    }
}