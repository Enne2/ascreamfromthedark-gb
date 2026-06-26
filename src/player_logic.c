#include "player_logic.h"
#include "globals.h"
#include "render.h"
#include <gb/gb.h>
#include <string.h>

// Delayed Auto-Shift variables
static uint8_t das_timer = 0;
static uint8_t das_active = 0;
#define DAS_DELAY 12
#define DAS_REPEAT 6
#define DAS_REPEAT_RUN 2   // DAS piu' rapido mentre si corre (il passo di corsa dura 8 frame)
#define RUN_STAMINA_COST 10
#define RUN_MIN_STAMINA 10

/**
 * Gestisce la logica di movimento del giocatore, i salti e le collisioni.
 *
 * Sviluppo & Scelte Architetturali:
 * 1. State Machine Rigida: Se `is_moving` è vero, ignoriamo qualsiasi altro input 
 *    finché l'animazione di transizione tra i tile (16 frame) non è completata.
 *    Questo ci assicura un movimento perfettamente a griglia "grid-based", in stile Pokémon o Zelda.
 * 2. Delayed Auto-Shift (DAS): Come in Tetris, se tieni premuto un tasto direzionale,
 *    c'è un ritardo iniziale (DAS_DELAY) seguito da ripetizioni veloci (DAS_REPEAT).
 *    Questo rende i controlli molto più fluidi e reattivi rispetto a una semplice lettura continua.
 * 3. Meccanica del Salto: Premendo A+Direzione, il giocatore può saltare *esattamente* 2 celle 
 *    più in là. Il codice verifica se la cella intermedia (+1) è un ostacolo (0) e se
 *    la cella di atterraggio (+2) è calpestabile. Consuma 60 di stamina per bilanciare il vantaggio tattico.
 * 4. Meccanica della Corsa: Premendo B+Direzione (con stamina >= 10) il giocatore si mette a correre:
 *    il passo dura 8 frame invece di 16 (move_progress incrementato di 2) e consuma 10 stamina per tile.
 *    Il DAS diventa piu' rapido (DAS_REPEAT_RUN) per incatenare i tile fluidamente. Se la stamina
 *    non basta, ripiega silenziosamente su camminata normale senza consumo.
 */
void update_player_movement(uint8_t keys, uint8_t prev_keys) {
    // --- Gestione della Stamina ---
    // Ricarica la stamina di 1 punto ogni `stamina_recharge_rate` frame (1/s al livello 1,
    // piu' lento ai livelli alti). `stamina_recharge_rate` e' impostato in engine_init.
    stamina_recharge_timer++;
    if (stamina_recharge_timer >= stamina_recharge_rate) {
        stamina_recharge_timer = 0;
        if (stamina < 100) {
            stamina++;
            update_stamina_display();
        }
    }

    // --- State Machine: Transizione Animazione ---
    // Se siamo nel mezzo di uno spostamento tra tile, calcoliamo i pixel interpolati
    if (is_moving) {
        // Corsa: il passo dura 8 frame (incremento 2) invece di 16 (incremento 1).
        // La formula LERP resta a punto fisso (>>4 == /16): move_progress raggiunge 16 in meta' tempo.
        move_progress += is_running ? 2 : 1;
        
        // Interpolazione lineare (LERP) da start a target
        int16_t px = start_px + (((target_px - start_px) * (int16_t)move_progress) >> 4); // >> 4 equivale a / 16
        int16_t py = start_py + (((target_py - start_py) * (int16_t)move_progress) >> 4);
        
        // Sincronizza la telecamera con i nuovi pixel sub-tile calcolati
        scroll_x = px - 64;
        scroll_y = py - 72;
        move_bkg(scroll_x, scroll_y);
        
        update_player_sprite();
        
        // A metà strada (frame 8/16), forziamo un ridisegno della mappa per aggiornare la nebbia (Fog of War)
        // in modo che il caricamento appaia fluido al giocatore
        if (move_progress == 8) {
            draw_map(target_lx, target_ly);
        }
        
        // Fine del movimento
        if (move_progress == 16) {
            is_moving = 0;
            is_jumping = 0;
            is_running = 0;
            player_lx = target_lx;
            player_ly = target_ly;
            
            // Snap matematico alla destinazione per prevenire derive dovute ad arrotondamenti
            int16_t final_px = (player_lx - player_ly) * 16 + 96;
            int16_t final_py = (player_lx + player_ly) * 8 + 16;
            scroll_x = final_px - 64;
            scroll_y = final_py - 72;
            move_bkg(scroll_x, scroll_y);
            
            draw_map(player_lx, player_ly);
            update_player_sprite();
            
            // Controllo Casella Vittoria (ID 2)
            if (maze[player_ly][player_lx] == 2) {
                // Livello 8 completato -> finale (gioco finito); altrimenti Going Deeper (lvl successivo).
                game_over = (level >= 8) ? 3 : 2;
                game_over_timer = 30; // Animazione di discesa (30 frame)
                descend_offset = 1; // avvia l'animazione di discesa nella botola
                update_stamina_display();
                // Lo schermo non viene pulito subito: l'animazione di discesa
                // avviene durante i 30 frame di game_over_timer.
            }
        }
        return; // Interrompe qui se stiamo camminando
    }

    // --- Lettura Controlli (Polling) con DAS ---
    uint8_t keys_pressed = keys & ~prev_keys; // Tasti premuti ESATTAMENTE in questo frame
    // La corsa (B tenuto + stamina) usa un DAS piu' corto per incatenare i tile fluidamente.
    uint8_t wants_run = (keys & J_B) && (stamina >= RUN_MIN_STAMINA);

    if (keys_pressed) {
        das_timer = wants_run ? DAS_REPEAT_RUN : DAS_DELAY;
        das_active = 1;
    } else if (keys && das_active) {
        // Se si tiene premuto un tasto...
        if (das_timer > 0) {
            das_timer--;
        }
        // Se il timer arriva a 0, emuliamo una pressione ripetuta
        if (das_timer == 0 && !is_moving) {
            das_timer = wants_run ? DAS_REPEAT_RUN : DAS_REPEAT;
            keys_pressed = keys; 
        }
    } else {
        das_active = 0;
    }

    // Traduzione Input Direzionale in Movimento Logico Grid-Based
    int8_t move_lx = 0;
    int8_t move_ly = 0;

    if (keys_pressed & J_RIGHT) {
        move_lx = 1; player_dir = 0; // Direzione Down-Right
    } else if (keys_pressed & J_LEFT) {
        move_lx = -1; player_dir = 2; // Direzione Up-Left
    } else if (keys_pressed & J_DOWN) {
        move_ly = 1; player_dir = 1; // Direzione Down-Left
    } else if (keys_pressed & J_UP) {
        move_ly = -1; player_dir = 3; // Direzione Up-Right
    }

    // Se stiamo cercando di muoverci
    if (move_lx != 0 || move_ly != 0) {
        // 1. Controllo Salto: Tasto A premuto insieme alla direzione
        if (keys & J_A) {
            // Il salto ci scaglia a distanza 2 lungo l'asse
            int8_t land_lx = player_lx + move_lx * 2;
            int8_t land_ly = player_ly + move_ly * 2;
            
            // Verifica che il salto cada all'interno del labirinto
            if (land_lx >= 0 && (uint8_t)land_lx < map_size && land_ly >= 0 && (uint8_t)land_ly < map_size) {
                // Condizioni del salto:
                // a) La cella intermedia DEVE essere un muro (maze == 0)
                // b) La cella di arrivo DEVE essere un pavimento o vittoria (maze == 1 o 2)
                // c) Devi avere abbastanza stamina (>= 60)
                if (maze[player_ly + move_ly][player_lx + move_lx] == 0 && (maze[land_ly][land_lx] == 1 || maze[land_ly][land_lx] == 2) && stamina >= 60) {
                    is_moving = 1;
                    is_jumping = 1; // Questo attiva l'arco parabolico in render.c
                    move_progress = 0;
                    stamina -= 60;
                    
                    start_lx = player_lx;
                    start_ly = player_ly;
                    target_lx = land_lx;
                    target_ly = land_ly;
                    
                    start_px = (start_lx - start_ly) * 16 + 96;
                    start_py = (start_lx + start_ly) * 8 + 16;
                    target_px = (target_lx - target_ly) * 16 + 96;
                    target_py = (target_lx + target_ly) * 8 + 16;
                    
                    // Suono Salto (Pitch Sweep Up sul Canale 1)
                    NR10_REG = 0x15; 
                    NR11_REG = 0x80;
                    NR12_REG = 0xF3; 
                    NR13_REG = 0x00; 
                    NR14_REG = 0xC3; 
                    
                    update_stamina_display();
                    update_player_sprite();
                    return;
                }
            }
            // Se le condizioni di salto falliscono, aggiorna semplicemente il frame per far girare il personaggio
            update_player_sprite();
        } 
        // 2. Movimento standard (Camminata o Corsa)
        else {
            int8_t new_lx = player_lx + move_lx;
            int8_t new_ly = player_ly + move_ly;

            if (new_lx >= 0 && (uint8_t)new_lx < map_size && new_ly >= 0 && (uint8_t)new_ly < map_size) {
                // Se la destinazione è pavimento normale o casella di vittoria
                if (maze[new_ly][new_lx] == 1 || maze[new_ly][new_lx] == 2) {
                    is_moving = 1;
                    move_progress = 0;
                    // Corsa: B + direzione con stamina sufficiente. Il passo dura 8 frame
                    // (vedi l'incremento di move_progress sopra) e costa 10 stamina per tile.
                    // Se la stamina non basta, ripiega silenziosamente su camminata normale.
                    if ((keys & J_B) && stamina >= RUN_MIN_STAMINA) {
                        is_running = 1;
                        stamina -= RUN_STAMINA_COST; // 10 stamina per tile (guardia sopra: stamina >= 10)
                        update_stamina_display();
                    } else {
                        is_running = 0;
                    }
                    start_lx = player_lx;
                    start_ly = player_ly;
                    target_lx = new_lx;
                    target_ly = new_ly;
                    
                    start_px = (start_lx - start_ly) * 16 + 96;
                    start_py = (start_lx + start_ly) * 8 + 16;
                    target_px = (target_lx - target_ly) * 16 + 96;
                    target_py = (target_lx + target_ly) * 8 + 16;
                }
            }
            // Qualunque cosa accada, aggiorniamo il frame dello sprite per riflettere la direzione
            update_player_sprite();
        }
    }
}
