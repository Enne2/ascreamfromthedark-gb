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

La stamina si ricarica di 1 punto ogni `stamina_recharge_rate` frame (60 ai livelli iniziali, 144 ai livelli avanzati — più lenta ai livelli alti).

## Salto Evasivo (A + direzione)

A+direzione → atterraggio **2 tile** più in là. Condizioni:
1. La cella intermedia (+1) **DEVE** essere un muro (`maze == 0`).
2. La cella di arrivo (+2) deve essere pavimento o botola.
3. Stamina ≥ 60 per un salto **sicuro**.

Costo: 60 stamina. Arco parabolico solo visivo: `y_offset = (move_progress * (16 - move_progress)) >> 2` (apice 16px a frame 8). La logica resta 2D grid-based.

### Salto rischioso (stamina < 60)

Con meno di 60 stamina il salto è **comunque consentito**, ma c'è una probabilità di cadere nel vuoto proporzionale alla stamina mancante:

```c
fall_chance = (60 - stamina) * 255 / 60;   // 60 sta = 0%, 30 sta = 50%, 0 sta = 255/256 (~99,6%)
roll = DIV_REG;                             // dado hardware, timing-dipendente
if (roll < fall_chance) → caduta
```

In caso di caduta il giocatore atterra sulla cella muro intermedia, precipita con un'animazione dedicata (suono di caduta su CH1+CH4) e muore (`game_over = 1`, timer 30 frame). Il dado usa `DIV_REG` (non il PRNG del labirinto): l'esito dipende dal frame esatto di pressione.

## Stamina

- 100 punti massimi.
- Ricarica: 1 punto ogni `stamina_recharge_rate` frame (60..144, scala col livello).
- Salto: costa 60 (salto sicuro); sotto 60 il salto è rischioso (vedi sopra).
- Corsa: costa 10/tile (da pieno, ~10 tile di corsa).
- Barra UI: 5 sprite in alto a destra, conversione `stamina*40/100` → pixel.

## Progressione Livelli

### Transizioni
- **Titolo → gioco**: `level = 1`, `engine_init()` genera il primo labirinto.
- **Vittoria (botola) + START**: `level++`, `engine_init()` genera il livello successivo.
- **Sconfitta + START**: si ricomincia dallo **stesso livello** raggiunto (non si azzera).
- **Finale (ultimo livello superato)**: `game_over = 3` invece di 2.

### Indicatore HUD
`L<n>` in alto a sinistra via 3 sprite (OAM 23-25) dall'asset `level.png` (glifi L, 0-9). Aggiornato ogni frame in `engine_update`; nascosto durante game over.

### Difficoltà scalabile (vedi anche `generation.md` e `ai.md`)
| Assi | Livelli iniziali | Livelli avanzati |
|------|-----------|-----------|
| Dimensione labirinto | 7×7 | 21×21 |
| Numero fantasmi | 1 | 8 |
| Cooldown fantasma | 60 frame | 11 frame |
| Ricarica stamina | 60 frame/pt | 144 frame/pt |
| Nebbia | 5×5 | 3×3 (dal L7) |

## Schermate di Fine Gioco

### Sconfitta (`game_over = 1`)
- 45 frame di "fermo immagine" drammatico (cattura da un fantasma) oppure 30 frame (caduta nel vuoto da salto rischioso).
- Poi: schermata testuale con font IBM — "THE DARK CLAIMED YOU / PRESS START AND RETRY" su sfondo nero (BGP invertito) + metasprite "GAME OVER".
- Musica: concerto tragico polifonico (128 note, noise percussion).
- START → ricomincia dallo stesso livello.

### Going Deeper (`game_over = 2`, livelli 1-7)
- 30 frame di dissolvenza.
- Schermata testuale col font IBM: "GOING DEEPER / LEVEL N".
- Musica: melodia misteriosa discendente (96 step).
- START → livello successivo.

### Finale (`game_over = 3`, ultimo livello)
- 30 frame di dissolvenza.
- Sfondo nero (BGP invertito 0x1B), font IBM ricaricato.
- Testo: messaggio finale (spoiler-free, da scoprire giocando).
- Musica dedicata: 192 step (24 accordi), lamento discendente in Re minore che cola nell'abisso, in loop.
- START → torna al titolo (nuova partita dal livello 1).