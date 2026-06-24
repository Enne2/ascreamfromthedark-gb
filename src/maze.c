#include "maze.h"
#include "globals.h"
#include <string.h>
#include <rand.h>

/**
 * Generates a randomized maze using a Depth-First Search (DFS) algorithm with backtracking.
 * 
 * Sviluppo & Scelte Architetturali:
 * 1. Perché DFS? Questo algoritmo è perfetto per labirinti garantendo che ogni cella sia 
 *    raggiungibile partendo dall'inizio (nessuna isola irraggiungibile).
 * 2. Il labirinto è una griglia MAP_SIZE x MAP_SIZE in cui le celle dispari (es. 1,1 o 3,3) 
 *    sono le stanze, mentre le celle pari sono i muri divisori. Il DFS scava i muri saltando
 *    di 2 in 2 e abbattendo il muro in mezzo.
 * 3. Abbiamo aggiunto una fase post-DFS che rimuove casualmente qualche muro rimasto (con
 *    il 15% di probabilità). Questo spezza la struttura "perfetta" del labirinto creando
 *    dei percorsi ciclici (loop). I loop sono vitali in un gioco con un nemico che ti insegue,
 *    permettendo al giocatore di aggirare il nemico scappando in cerchio.
 * 4. La casella della VITTORIA viene piazzata alla fine. Usiamo la "Distanza di Manhattan"
 *    (somma della distanza X e Y) dalla partenza (1,1) per assicurarci che il traguardo 
 *    sia la casella più lontana in assoluto.
 */
void generate_maze(void) {
    // 1. Inizializziamo l'intera mappa a 0 (che rappresenta un Muro / Spazio Vuoto)
    memset(maze, 0, sizeof(maze));
    
    // Stack array per il backtracking. La griglia 7x7 ha al massimo 49 celle dispari (stanze).
    uint8_t stack_x[49];
    uint8_t stack_y[49];
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
        if (cy <= MAP_SIZE - 4 && maze[cy + 2][cx] == 0) {
            nx[count] = cx; ny[count] = cy + 2; count++;
        }
        // Sinistra
        if (cx >= 3 && maze[cy][cx - 2] == 0) {
            nx[count] = cx - 2; ny[count] = cy; count++;
        }
        // Destra
        if (cx <= MAP_SIZE - 4 && maze[cy][cx + 2] == 0) {
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
            
            // Abbattiamo il muro nel mezzo (calcolato facendo la media aritmetica delle coordinate)
            maze[(cy + ny[dir]) / 2][(cx + nx[dir]) / 2] = 1;
            
            // Spostiamo la posizione corrente sul vicino scelto
            cx = nx[dir];
            cy = ny[dir];
            maze[cy][cx] = 1;
        } 
        // Se non ci sono vicini, torna indietro prendendo l'ultima cella salvata dallo stack
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
    
    // FASE 2: Riapriamo casualmente dei muri per creare percorsi alternativi e loop (15% chance).
    // Questo è cruciale per la giocabilità: permette al giocatore di aggirare l'inseguitore!
    for (uint8_t y = 1; y < MAP_SIZE - 1; y++) {
        for (uint8_t x = 1; x < MAP_SIZE - 1; x++) {
            if (maze[y][x] == 0) {
                // Se la casella è un muro che connette orizzontalmente o verticalmente due corridoi
                if ((maze[y][x - 1] == 1 && maze[y][x + 1] == 1) ||
                    (maze[y - 1][x] == 1 && maze[y + 1][x] == 1)) {
                    // Genera numero casuale tra 0 e 99. Se < 15, trasforma in pavimento.
                    if ((rand() % 100) < 15) {
                        maze[y][x] = 1;
                    }
                }
            }
        }
    }
    
    // FASE 3: Posizionamento della Botola (Traguardo).
    // La botola viene piazzata su una cella calpestabile a "sufficiente distanza"
    // dalla casella di partenza del giocatore (1,1), cosi' che il traguardo sia
    // sempre lontano ma possa trovarsi su una qualunque tile del labirinto,
    // non piu' vincolato al bordo sud. Usiamo la distanza di Chebyshev
    // (consistente con il resto dell'engine: fog of war, attivazione nemico).
#define MIN_GOAL_DIST 3
    uint8_t valid_x[MAP_SIZE * MAP_SIZE];
    uint8_t valid_y[MAP_SIZE * MAP_SIZE];
    uint8_t num_valid = 0;

    for (uint8_t y = 1; y < MAP_SIZE - 1; y++) {
        for (uint8_t x = 1; x < MAP_SIZE - 1; x++) {
            if (maze[y][x] == 1) {
                int8_t dx = (int8_t)x - 1;
                int8_t dy = (int8_t)y - 1;
                if (dx < 0) dx = -dx;
                if (dy < 0) dy = -dy;
                int8_t dist = (dx > dy) ? dx : dy;
                if (dist >= MIN_GOAL_DIST) {
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
        // Fallback estremo: nessuna cella a sufficienza distante (teoricamente
        // impossibile in un perfect maze 7x7 con partenza 1,1, ma difensivo).
        // Sceglie la cella calpestabile piu' lontana in assoluto da (1,1).
        uint8_t best_x = MAP_SIZE - 2;
        uint8_t best_y = MAP_SIZE - 2;
        int8_t best_dist = -1;
        for (uint8_t y = 1; y < MAP_SIZE - 1; y++) {
            for (uint8_t x = 1; x < MAP_SIZE - 1; x++) {
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
