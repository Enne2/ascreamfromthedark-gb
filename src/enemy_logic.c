#include "enemy_logic.h"
#include "globals.h"
#include "render.h" // For update_stamina_display (called on fatal collision)
#include <gb/gb.h>

// Tile graphics required for metasprites
#include "player.h"
#include "enemy.h"

/**
 * Gestisce l'intelligenza artificiale e il rendering dei fantasmi (nemici).
 *
 * Sviluppo & Scelte Architetturali:
 * 1. Multi-entity: fino a MAX_ENEMIES (8) fantasmi coesistenti. Lo stato di ciascuno
 *    e' in array indicizzati (enemy_lx[i], enemy_is_moving[i], ...). Il numero attivo
 *    e' num_enemies (= livello, capped). Ogni fantasma usa 2 slot OAM (sprite 8x16)
 *    a partire da OAM 2 + i*2 (il player usa 0-1).
 * 2. Cooldown: dopo ogni passo (16 frame di LERP) il fantasma aspetta `enemy_step_cooldown`
 *    frame prima del prossimo (scalato col livello: piu' breve = piu' veloce). I cooldown
 *    iniziali sono sfasati (i*8) cosi' non si muovono in sincrono.
 * 3. Pathfinding Greedy (non A*): per ogni fantasma, tra le 4 celle adiacenti calpestabili
 *    sceglie quella che minimizza la distanza al quadrato verso il giocatore (no sqrt, no
 *    heap: sostenibile su 4 MHz anche con 8 fantasmi). Difetto voluto: si incastra nei
 *    vicoli a U -> dinamica di gioco per seminarli.
 * 4. Attivazione: il fantasma insegue solo se entro il raggio di nebbia (Chebyshev <=
 *    fog_radius), coerente col fog of war.
 * 5. Collisione Pixel-Perfect: la morte scatta se i pixel fisici di un qualunque fantasma
 *    si sovrappongono a quelli del giocatore (|dx|<12, |dy|<6).
 */
void update_enemy_logic(void) {
    // Posizione pixel del giocatore (interpolata se in movimento), usata per la collisione.
    int16_t p_px = is_moving ? (start_px + (((target_px - start_px) * (int16_t)move_progress) >> 4))
                             : ((player_lx - player_ly) * 16 + 96);
    int16_t p_py = is_moving ? (start_py + (((target_py - start_py) * (int16_t)move_progress) >> 4))
                             : ((player_lx + player_ly) * 8 + 16);

    for (uint8_t i = 0; i < num_enemies; i++) {
        // 1. Aggiorna l'interpolazione del movimento visivo
        if (enemy_is_moving[i]) {
            enemy_move_progress[i]++;
            if (enemy_move_progress[i] == 16) {
                enemy_is_moving[i] = 0;
                enemy_lx[i] = enemy_target_lx[i];
                enemy_ly[i] = enemy_target_ly[i];
                // Pausa prima del prossimo passo (scalata col livello).
                enemy_cooldown[i] = enemy_step_cooldown;
            }
        }

        // 2. Decrementa il timer di riposo
        if (enemy_cooldown[i] > 0) {
            enemy_cooldown[i]--;
        }

        // 3. AI PATHFINDING (greedy) se pronto a muoversi
        if (!enemy_is_moving[i] && enemy_cooldown[i] == 0) {
            int8_t dx = (int8_t)player_lx - (int8_t)enemy_lx[i];
            int8_t dy = (int8_t)player_ly - (int8_t)enemy_ly[i];
            int8_t abs_dx = (dx < 0) ? -dx : dx;
            int8_t abs_dy = (dy < 0) ? -dy : dy;
            int8_t dist = (abs_dx > abs_dy) ? abs_dx : abs_dy;

            // Insegue solo se entro il raggio di nebbia.
            if (dist <= (int8_t)fog_radius) {
                int8_t best_nx = (int8_t)enemy_lx[i];
                int8_t best_ny = (int8_t)enemy_ly[i];
                int16_t min_dist_sq = (int16_t)dx * dx + (int16_t)dy * dy;

                if (enemy_lx[i] + 1 < map_size && maze[enemy_ly[i]][enemy_lx[i] + 1] != 0) {
                    int8_t ndx = (int8_t)player_lx - (int8_t)(enemy_lx[i] + 1);
                    int16_t d_sq = (int16_t)ndx * ndx + (int16_t)dy * dy;
                    if (d_sq < min_dist_sq) { min_dist_sq = d_sq; best_nx = enemy_lx[i] + 1; best_ny = enemy_ly[i]; }
                }
                if (enemy_ly[i] + 1 < map_size && maze[enemy_ly[i] + 1][enemy_lx[i]] != 0) {
                    int8_t ndy = (int8_t)player_ly - (int8_t)(enemy_ly[i] + 1);
                    int16_t d_sq = (int16_t)dx * dx + (int16_t)ndy * ndy;
                    if (d_sq < min_dist_sq) { min_dist_sq = d_sq; best_nx = enemy_lx[i]; best_ny = enemy_ly[i] + 1; }
                }
                if (enemy_lx[i] > 0 && maze[enemy_ly[i]][enemy_lx[i] - 1] != 0) {
                    int8_t ndx = (int8_t)player_lx - (int8_t)(enemy_lx[i] - 1);
                    int16_t d_sq = (int16_t)ndx * ndx + (int16_t)dy * dy;
                    if (d_sq < min_dist_sq) { min_dist_sq = d_sq; best_nx = enemy_lx[i] - 1; best_ny = enemy_ly[i]; }
                }
                if (enemy_ly[i] > 0 && maze[enemy_ly[i] - 1][enemy_lx[i]] != 0) {
                    int8_t ndy = (int8_t)player_ly - (int8_t)(enemy_ly[i] - 1);
                    int16_t d_sq = (int16_t)dx * dx + (int16_t)ndy * ndy;
                    if (d_sq < min_dist_sq) { min_dist_sq = d_sq; best_nx = enemy_lx[i]; best_ny = enemy_ly[i] - 1; }
                }

                if (best_nx != (int8_t)enemy_lx[i] || best_ny != (int8_t)enemy_ly[i]) {
                    enemy_is_moving[i] = 1;
                    enemy_move_progress[i] = 0;
                    enemy_start_lx[i] = (int8_t)enemy_lx[i];
                    enemy_start_ly[i] = (int8_t)enemy_ly[i];
                    enemy_target_lx[i] = best_nx;
                    enemy_target_ly[i] = best_ny;
                    enemy_start_px[i] = (enemy_start_lx[i] - enemy_start_ly[i]) * 16 + 96;
                    enemy_start_py[i] = (enemy_start_lx[i] + enemy_start_ly[i]) * 8 + 16;
                    enemy_target_px[i] = (enemy_target_lx[i] - enemy_target_ly[i]) * 16 + 96;
                    enemy_target_py[i] = (enemy_target_lx[i] + enemy_target_ly[i]) * 8 + 16;
                }
            }
        }

        // 4. RENDERING (telecamera relativa)
        int16_t enemy_px, enemy_py;
        if (enemy_is_moving[i]) {
            enemy_px = enemy_start_px[i] + (((enemy_target_px[i] - enemy_start_px[i]) * (int16_t)enemy_move_progress[i]) >> 4);
            enemy_py = enemy_start_py[i] + (((enemy_target_py[i] - enemy_start_py[i]) * (int16_t)enemy_move_progress[i]) >> 4);
        } else {
            enemy_px = (enemy_lx[i] - enemy_ly[i]) * 16 + 96;
            enemy_py = (enemy_lx[i] + enemy_ly[i]) * 8 + 16;
        }

        int16_t enemy_screen_x = ((enemy_px - scroll_x) & 255) + 24;
        int16_t enemy_screen_y = ((enemy_py - scroll_y) & 255) + 16;

        // Visibilita': solo se entro il raggio di nebbia e on-screen.
        int8_t edx = (int8_t)player_lx - (int8_t)enemy_lx[i];
        int8_t edy = (int8_t)player_ly - (int8_t)enemy_ly[i];
        if (edx < 0) edx = -edx;
        if (edy < 0) edy = -edy;
        uint8_t ep_dist = (edx > edy) ? edx : edy;

        if (ep_dist <= fog_radius && enemy_screen_x >= -8 && enemy_screen_x <= 168 && enemy_screen_y >= -8 && enemy_screen_y <= 152) {
            move_metasprite(enemy_metasprites[0], player_TILE_COUNT, 2 + i * 2, enemy_screen_x, enemy_screen_y);
        } else {
            move_metasprite(enemy_metasprites[0], player_TILE_COUNT, 2 + i * 2, 0, 0);
        }

        // 5. COLLISIONE FATALE (pixel-perfect) contro questo fantasma
        int16_t dxc = p_px - enemy_px;
        int16_t dyc = p_py - enemy_py;
        if (dxc < 0) dxc = -dxc;
        if (dyc < 0) dyc = -dyc;
        if (dxc < 12 && dyc < 6) {
            game_over = 1;
            game_over_timer = 45;
            update_stamina_display(); // nasconde l'HUD (game_over attivo)
            // Sound effect della cattura (slide down sul canale 1)
            NR10_REG = 0x1E;
            NR11_REG = 0x10;
            NR12_REG = 0xF3;
            NR13_REG = 0x00;
            NR14_REG = 0xC6;
            return; // un fantasma ti ha preso: basta per questo frame
        }
    }
}