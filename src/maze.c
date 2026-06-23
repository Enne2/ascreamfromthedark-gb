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
    
    // FASE 3: Calcoliamo il traguardo (Casella di Vittoria).
    // Invece della coordinata più lontana, scegliamo un punto casuale
    // lungo il bordo inferiore del labirinto (y = MAP_SIZE - 2).
    // Questo permette alla scala di apparire ovunque sul bordo sud.
    uint8_t valid_x[MAP_SIZE];
    uint8_t num_valid = 0;
    
    for (uint8_t x = 1; x < MAP_SIZE - 1; x++) {
        if (maze[MAP_SIZE - 2][x] == 1) {
            valid_x[num_valid] = x;
            num_valid++;
        }
    }
    
    if (num_valid > 0) {
        uint8_t target_x = valid_x[rand() % num_valid];
        maze[MAP_SIZE - 2][target_x] = 2;
        stairs_lx = target_x;
        stairs_ly = MAP_SIZE - 2;
    } else {
        // Fallback estremo se la riga in fondo fosse inaccessibile
        maze[MAP_SIZE - 2][MAP_SIZE - 2] = 2;
        stairs_lx = MAP_SIZE - 2;
        stairs_ly = MAP_SIZE - 2;
    }
}
