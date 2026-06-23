#include "enemy_logic.h"
#include "globals.h"
#include "render.h" // For update_stamina_display
#include <gb/gb.h>

// Tile graphics required for metasprites
#include "player.h"
#include "enemy.h"

/**
 * Gestisce l'intelligenza artificiale (AI) e il rendering del nemico (il fantasma).
 *
 * Sviluppo & Scelte Architetturali:
 * 1. Cooldown System: Il fantasma fa "passi" esatti sulla griglia proprio come il giocatore.
 *    Tuttavia, se si muovesse a ogni frame, sarebbe impossibile scappare. 
 *    Abbiamo implementato un timer di `enemy_cooldown` (60 frame = 1 secondo) di pausa 
 *    tra un passo e l'altro. Il giocatore cammina/salta più velocemente, creando una 
 *    tensione in cui devi pianificare i tuoi balzi per seminarlo.
 * 2. Pathfinding (Ricerca del Percorso): Invece di usare A* (A-Star) che consumerebbe
 *    troppa RAM e CPU per un Game Boy a 8-bit, il fantasma usa una logica "Greedy".
 *    Calcola la distanza al quadrato verso il giocatore per ciascuna delle 4 direzioni
 *    valide (muri permettendo). Sceglie la direzione che *minimizza* questa distanza.
 *    Non essendo A*, può incastrarsi in vicoli ciechi a forma di "U", che è esattamente
 *    una debolezza voluta per permettere al giocatore di seminarlo usando il level design.
 * 3. Collisione Pixel-Perfect: Anche se logica e pathfinding sono su griglia (Grid-Based),
 *    la Morte scatta solo se i *pixel* fisici a schermo dei due sprite si sovrappongono.
 */
void update_enemy_logic(void) {
    // 1. Aggiorna l'interpolazione del movimento visivo del fantasma
    if (enemy_is_moving) {
        enemy_move_progress++;
        if (enemy_move_progress == 16) {
            // Movimento completato
            enemy_is_moving = 0;
            enemy_lx = enemy_target_lx;
            enemy_ly = enemy_target_ly;
            // Imposta una pausa di 1 secondo prima del prossimo passo (Bilanciamento difficoltà)
            enemy_cooldown = 60; 
        }
    }

    // 2. Decrementa il timer di riposo se non si sta muovendo
    if (enemy_cooldown > 0) {
        enemy_cooldown--;
    }

    // 3. AI PATHFINDING: Calcola il prossimo passo se è pronto a muoversi
    if (!enemy_is_moving && enemy_cooldown == 0) {
        // Calcola Distanza di Chebyshev logica dal giocatore per sapere se siamo "vicini"
        int8_t dx = (int8_t)player_lx - (int8_t)enemy_lx;
        int8_t dy = (int8_t)player_ly - (int8_t)enemy_ly;
        int8_t abs_dx = (dx < 0) ? -dx : dx;
        int8_t abs_dy = (dy < 0) ? -dy : dy;
        int8_t dist = (abs_dx > abs_dy) ? abs_dx : abs_dy;
        
        // L'AI "si sveglia" e inizia a inseguirti solo se è entro 2 celle di distanza 
        // (cioè è entrato nel tuo cono visivo di nebbia)
        if (dist <= 2) {
            int8_t best_nx = enemy_lx;
            int8_t best_ny = enemy_ly;
            
            // Inizializza con la distanza Euclidea al QUADRATO (x^2 + y^2) corrente.
            // Non usiamo la radice quadrata (sqrt) perché è un calcolo pesantissimo su Game Boy.
            // Il quadrato della distanza conserva le proporzioni perfette per il confronto (min_dist).
            int16_t min_dist_sq = (int16_t)dx * dx + (int16_t)dy * dy;
            
            // Controllo 1: Direzione Down-Right (+1 X)
            if (enemy_lx + 1 < MAP_SIZE && maze[enemy_ly][enemy_lx + 1] != 0) {
                int8_t ndx = (int8_t)player_lx - (int8_t)(enemy_lx + 1);
                int8_t ndy = (int8_t)player_ly - (int8_t)enemy_ly;
                int16_t d_sq = (int16_t)ndx * ndx + (int16_t)ndy * ndy;
                if (d_sq < min_dist_sq) { min_dist_sq = d_sq; best_nx = enemy_lx + 1; best_ny = enemy_ly; }
            }
            // Controllo 2: Direzione Down-Left (+1 Y)
            if (enemy_ly + 1 < MAP_SIZE && maze[enemy_ly + 1][enemy_lx] != 0) {
                int8_t ndx = (int8_t)player_lx - (int8_t)enemy_lx;
                int8_t ndy = (int8_t)player_ly - (int8_t)(enemy_ly + 1);
                int16_t d_sq = (int16_t)ndx * ndx + (int16_t)ndy * ndy;
                if (d_sq < min_dist_sq) { min_dist_sq = d_sq; best_nx = enemy_lx; best_ny = enemy_ly + 1; }
            }
            // Controllo 3: Direzione Up-Left (-1 X)
            if (enemy_lx > 0 && maze[enemy_ly][enemy_lx - 1] != 0) {
                int8_t ndx = (int8_t)player_lx - (int8_t)(enemy_lx - 1);
                int8_t ndy = (int8_t)player_ly - (int8_t)enemy_ly;
                int16_t d_sq = (int16_t)ndx * ndx + (int16_t)ndy * ndy;
                if (d_sq < min_dist_sq) { min_dist_sq = d_sq; best_nx = enemy_lx - 1; best_ny = enemy_ly; }
            }
            // Controllo 4: Direzione Up-Right (-1 Y)
            if (enemy_ly > 0 && maze[enemy_ly - 1][enemy_lx] != 0) {
                int8_t ndx = (int8_t)player_lx - (int8_t)enemy_lx;
                int8_t ndy = (int8_t)player_ly - (int8_t)(enemy_ly - 1);
                int16_t d_sq = (int16_t)ndx * ndx + (int16_t)ndy * ndy;
                if (d_sq < min_dist_sq) { min_dist_sq = d_sq; best_nx = enemy_lx; best_ny = enemy_ly - 1; }
            }
            
            // Se abbiamo trovato un percorso migliore (Strictly closer)
            if (best_nx != (int8_t)enemy_lx || best_ny != (int8_t)enemy_ly) {
                enemy_is_moving = 1;
                enemy_move_progress = 0;
                enemy_start_lx = enemy_lx;
                enemy_start_ly = enemy_ly;
                enemy_target_lx = best_nx;
                enemy_target_ly = best_ny;
                
                // Preparazione coordinate pixel hardware per l'interpolazione fluida
                enemy_start_px = (enemy_start_lx - enemy_start_ly) * 16 + 96;
                enemy_start_py = (enemy_start_lx + enemy_start_ly) * 8 + 16;
                enemy_target_px = (enemy_target_lx - enemy_target_ly) * 16 + 96;
                enemy_target_py = (enemy_target_lx + enemy_target_ly) * 8 + 16;
            }
        }
    }

    // 4. RENDERING DEL NEMICO (Telecamera relativa)
    // Recuperiamo i pixel assoluti
    int16_t enemy_px, enemy_py;
    if (enemy_is_moving) {
        enemy_px = enemy_start_px + (((enemy_target_px - enemy_start_px) * (int16_t)enemy_move_progress) >> 4);
        enemy_py = enemy_start_py + (((enemy_target_py - enemy_start_py) * (int16_t)enemy_move_progress) >> 4);
    } else {
        enemy_px = (enemy_lx - enemy_ly) * 16 + 96;
        enemy_py = (enemy_lx + enemy_ly) * 8 + 16;
    }
    
    // Il motore renderizza lo sfondo scrollando, ma gli SPRITE devono essere disegnati a mano.
    // Togliamo il valore di scroll della telecamera (scroll_x, scroll_y) dalla posizione assoluta.
    // +24 e +16 sono offset per l'allineamento hardware OAM del Game Boy per le griglie 16x16.
    int16_t enemy_screen_x = ((enemy_px - scroll_x) & 255) + 24;
    int16_t enemy_screen_y = ((enemy_py - scroll_y) & 255) + 16;
    
    // Mostriamo lo sprite solo se è all'interno della griglia logica visibile (distanza <= 2)
    int8_t edx = (int8_t)player_lx - (int8_t)enemy_lx;
    int8_t edy = (int8_t)player_ly - (int8_t)enemy_ly;
    if (edx < 0) edx = -edx;
    if (edy < 0) edy = -edy;
    uint8_t ep_dist = (edx > edy) ? edx : edy;
    
    // Il limite x=168 e y=152 assicura di nascondere gli sprite appena fuori dai bordi fisici
    if (ep_dist <= 2 && enemy_screen_x >= -8 && enemy_screen_x <= 168 && enemy_screen_y >= -8 && enemy_screen_y <= 152) {
        // Disegna il metasprite del Fantasma usando gli offset di memoria generati in enemy.h
        move_metasprite(enemy_metasprites[0], player_TILE_COUNT, 4, enemy_screen_x, enemy_screen_y); 
    } else {
        // Nasconde lo sprite spostandolo a coordinate (0,0) offscreen 
        move_metasprite(enemy_metasprites[0], player_TILE_COUNT, 4, 0, 0); 
    }

    // 5. COLLISIONE FATALE (Player Hitbox check)
    // Per calcolare esattamente il game over, usiamo la posizione *Pixel* di entrambi.
    int16_t p_px = is_moving ? (start_px + (((target_px - start_px) * (int16_t)move_progress) >> 4)) : ((player_lx - player_ly) * 16 + 96);
    int16_t p_py = is_moving ? (start_py + (((target_py - start_py) * (int16_t)move_progress) >> 4)) : ((player_lx + player_ly) * 8 + 16);

    int16_t dx_collision = p_px - enemy_px;
    int16_t dy_collision = p_py - enemy_py;
    if (dx_collision < 0) dx_collision = -dx_collision;
    if (dy_collision < 0) dy_collision = -dy_collision;

    // Se i pixel centrali sono vicini (X < 12 e Y < 6), scatena il GAME OVER
    if (dx_collision < 12 && dy_collision < 6) {
        game_over = 1; // 1 = Defeat
        game_over_timer = 45; // Fermo immagine drammatico per 45 frame (~0.7s) prima del menu nero
        update_stamina_display(); // Aggiornando con game_over=1 l'HUD scompare istantaneamente
        
        // Esegue il Sound Effect della cattura: Suono profondo a caduta (Slide Down) sul Canale 1
        NR10_REG = 0x1E; // sweep register: shift down
        NR11_REG = 0x10; // 25% duty cycle
        NR12_REG = 0xF3; // volume alto, calo rapido (envelope decrease)
        NR13_REG = 0x00; // frequenza bassa
        NR14_REG = 0xC6; // trigger 
    }
}
