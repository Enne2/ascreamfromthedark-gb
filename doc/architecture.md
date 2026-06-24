# Architettura di Base

## Overview

Il progetto è un gioco completo per Game Boy (DMG/CGB) con 8 livelli di difficoltà crescente, multi-nemico, audio polifonico e finale tragico. Tutto in 32 KB di ROM e 8 KB di WRAM.

## Organizzazione del progetto

```
gameboy-hello-iso/
├── assets/          # PNG sorgenti (sprite, tileset, schermate)
├── scripts/         # Script Python per generazione/quantizzazione asset
├── src/             # Codice C + asset generati da png2asset
├── doc/             # Documentazione tecnica
├── build/           # Output compilazione (ROM .gb)
├── Makefile         # Build system (GBDK lcc + png2asset)
└── README.md
```

## Modularizzazione del codice C

Il gioco nasceva da un monolite `engine.c` di 1000+ righe, poi rifattorizzato in moduli a singola responsabilità:

| File | Righe | Ruolo |
|------|-------|-------|
| `main.c` | ~30 | Entry point, loop VBL, macchina a stati `app_state` (0=title, 1=game). |
| `engine.c` | ~290 | "Direttore d'orchestra": `title_init/update`, `engine_init`, `engine_update`. Gestisce game over (sconfitta/vittoria/finale), schermate di transizione. |
| `globals.c/h` | ~80 | Stato globale centralizzato: mappa, camera, player, enemy (array), stamina, level, fog_radius, map_size. |
| `maze.c` | ~140 | Generazione procedurale DFS + loop + botola. |
| `player_logic.c` | ~200 | Input, DAS, state machine, camminata, corsa, salto, stamina. |
| `enemy_logic.c` | ~140 | AI greedy multi-entity, cooldown scalabile, rendering nemici, hitbox. |
| `render.c` | ~280 | Proiezione isometrica, fog of war scalabile, auto-tiling multi-pass, flush dinamico, stamina UI, level HUD, sprite player. |
| `sound.c` | ~430 | Sequencer audio via VBL: title (112 note), gameplay (96), gameover (128), finale (192, loop). |

Asset generati da `png2asset`: `tiles.c`, `player.c`, `enemy.c`, `gameover.c`, `stamina.c`, `level.c`, `claimed.c`, `title_bg.c`.

## Stato globale (`globals.h`)

Tutte le variabili mutabili sono centralizzate in `globals.c` ed esposte via `extern` in `globals.h`. Questo evita dipendenze circolari tra moduli C (render ha bisogno di player, player ha bisogno di maze, ecc.).

### Variabili chiave

| Variabile | Tipo | Descrizione |
|-----------|------|-------------|
| `app_state` | uint8_t | 0 = title, 1 = gameplay |
| `game_over` | volatile uint8_t | 0 = playing, 1 = defeat, 2 = victory/Going Deeper, 3 = finale |
| `game_over_timer` | volatile uint8_t | Delay drammatico prima della schermata di fine |
| `map_size` | uint8_t | Dimensione corrente del labirinto (7..21, cresce col livello) |
| `maze[21][21]` | uint8_t | 0 = muro, 1 = pavimento, 2 = botola |
| `fog_radius` | uint8_t | Raggio visibilità Chebyshev (2 normalmente, 1 dal livello 7) |
| `level` | uint8_t | Livello corrente (1..8) |
| `num_enemies` | uint8_t | Numero fantasmi attivi (= livello, capped 8) |
| `enemy_step_cooldown` | uint8_t | Pausa tra passi del fantasma (60..11, scala col livello) |
| `stamina_recharge_rate` | uint8_t | Frame per +1 stamina (60..144, scala col livello) |
| `stamina` | uint8_t | 0..100, potenzia salto (60) e corsa (10/tile) |
| `enemy_lx[8]` ecc. | array | Stato multi-nemico (fino a 8 fantasmi) |

## Pipeline asset (Python → C)

1. **Script Python** (`scripts/generate_assets.py`, `generate_enemy.py`, `generate_level.py`) creano i PNG sorgenti da matrici di pixel, usando la palette GB a 4 colori.
2. **`png2asset`** (tool GBDK) converte ogni PNG in `src/*.c` (tile data + map + metasprite).
3. **`lcc`** (frontend SDCC) compila e linka tutti i `.c` nella ROM finale `build/hello_iso.gb`.

Il `Makefile` orchestra questo processo: `make clean && make` rigenera tutto da zero.

## Vincoli hardware

| Risorsa | Limite | Utilizzo attuale |
|---------|--------|------------------|
| ROM | 32 KB | ~32 KB (pieno) |
| WRAM | 8 KB | ~3 KB (maze 441B + map_buffer 1KB + enemy arrays 88B + statici maze.c ~1KB + globals) |
| VRAM tile data | 384 tile (6 KB) | ~200 tile (BG + sprite condivisi) |
| OAM (sprite) | 40 sprite | ~27 (player 2 + enemies 16 + stamina 5 + HUD 3 + gameover 10) |
| Sprite/scanline | 10 | Rispettato (HUD in alto, player al centro, nemici sparsi) |
| CPU | 4.19 MHz | LERP a punto fisso, no float, no sqrt |