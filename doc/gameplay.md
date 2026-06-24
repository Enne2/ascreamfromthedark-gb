# Fisica e Controlli del Giocatore

## State Machine (Grid-Based)

Il movimento è rigidamente vincolato alla griglia (stile Zelda/Pokémon). Durante `is_moving` (interpolazione LERP su 16 frame, o 8 in corsa) ogni input è ignorato. Questo garantisce movimento perfettamente allineato, senza scivolamenti diagonali.

## LERP a Punto Fisso

```c
px = start_px + ((target_px - start_px) * move_progress) >> 4;  // >>4 = /16
```

Tutto a punto fisso (no float, no divisione hardware). In corsa `move_progress += 2` → il passo dura 8 frame invece di 16, ma la formula LERP `>>4` resta invariata (raggiunge il target in metà tempo).

## Delayed Auto-Shift (DAS)

Come in Tetris: il primo tocco muove subito; tenendo premuto, l'input è ignorato per `DAS_DELAY = 12` frame, poi si ripete ogni `DAS_REPEAT = 6` frame (camminata) o `DAS_REPEAT_RUN = 2` (corsa, per incatenare i tile fluidamente).

`keys_pressed = keys & ~prev_keys` rileva il fronte di salita (pressione esatta).

## Camminata

Direzione → `move_lx/move_ly` (±1 su un asse). Validazione: `maze[new_ly][new_lx] == 1 || == 2` (pavimento o botola). Se valida, `is_moving = 1`, `move_progress = 0`, start/target impostati.

## Corsa (B + direzione)

Tenendo **B** + direzione con stamina ≥ 10:
- Il passo dura **8 frame** invece di 16 (`is_running = 1`, `move_progress += 2`).
- Costo: **10 stamina per tile**.
- DAS più rapido (`DAS_REPEAT_RUN = 2`) per incatenare i tile fluidamente.
- Se stamina < 10: ripiega silenziosamente su camminata normale (0 costo).
- La corsa si riattiva da sola quando la stamina torna ≥ 10.

La stamina si ricarica di 1 punto ogni `stamina_recharge_rate` frame (60 al livello 1, 144 al livello 8 — più lenta ai livelli alti).

## Salto Evasivo (A + direzione)

A+direzione → atterraggio **2 tile** più in là. Condizioni:
1. La cella intermedia (+1) **DEVE** essere un muro (`maze == 0`).
2. La cella di arrivo (+2) deve essere pavimento o botola.
3. Stamina ≥ 60.

Costo: 60 stamina. Arco parabolico solo visivo: `y_offset = (move_progress * (16 - move_progress)) >> 2` (apice 16px a frame 8). La logica resta 2D grid-based.

## Stamina

- 100 punti massimi.
- Ricarica: 1 punto ogni `stamina_recharge_rate` frame (60..144, scala col livello).
- Salto: costa 60 (disabilita ulteriori balzi per ~1 min).
- Corsa: costa 10/tile (da pieno, ~10 tile di corsa).
- Barra UI: 5 sprite in alto a destra, conversione `stamina*40/100` → pixel.

## Progressione Livelli (8 livelli + finale)

### Transizioni
- **Titolo → gioco**: `level = 1`, `engine_init()` genera il primo labirinto.
- **Vittoria (botola) + START**: `level++`, `engine_init()` genera il livello successivo.
- **Sconfitta + START**: si ricomincia dallo **stesso livello** raggiunto (non si azzera).
- **Finale (livello 8 superato)**: `game_over = 3` invece di 2.

### Indicatore HUD
`L<n>` in alto a sinistra via 3 sprite (OAM 23-25) dall'asset `level.png` (glifi L, 0-9). Aggiornato ogni frame in `engine_update`; nascosto durante game over.

### Difficoltà scalabile (vedi anche `generation.md` e `ai.md`)
| Assi | Livello 1 | Livello 8 |
|------|-----------|-----------|
| Dimensione labirinto | 7×7 | 21×21 |
| Numero fantasmi | 1 | 8 |
| Cooldown fantasma | 60 frame | 11 frame |
| Ricarica stamina | 60 frame/pt | 144 frame/pt |
| Nebbia | 5×5 | 3×3 (dal L7) |

## Schermate di Fine Gioco

### Sconfitta (`game_over = 1`)
- 45 frame di "fermo immagine" drammatico.
- Poi: schermata `claimed.png` a tutto schermo + metasprite "GAME OVER".
- Musica: concerto tragico polifonico (128 note, noise percussion).
- START → ricomincia dallo stesso livello.

### Going Deeper (`game_over = 2`, livelli 1-7)
- 30 frame di dissolvenza.
- Schermata testuale col font IBM: "GOING DEEPER / LEVEL N".
- Musica: melodia misteriosa discendente (96 step).
- START → livello successivo.

### Finale tragico (`game_over = 3`, livello 8)
- 30 frame di dissolvenza.
- Sfondo nero (BGP invertito 0x1B), font IBM ricaricato.
- Testo: messaggio tragico (spoiler-free, da scoprire giocando).
- Musica dedicata: 192 step (24 accordi), lamento discendente in Re minore che cola nell'abisso, in loop.
- START → torna al titolo (nuova partita dal livello 1).