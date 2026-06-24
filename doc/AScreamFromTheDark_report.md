# A Scream from the Dark — Report Tecnico Approfondito

> Survival-horror procedurale isometrico per Game Boy (DMG/CGB), scritto in C con **GBDK-2020** (SDCC).
> Repository: `gameboy-hello-iso` · ROM: `build/hello_iso.gb` (32 KB).
> ~6500 righe C/H + ~2000 righe Python (pipeline asset).

---

## 1. Identità del gioco

"A Scream from the Dark" è un survival-horror procedurale in prospettiva isometrica 2.5D. Sei imprigionato in un labirinto generato casualmente, illuminato solo da un ristretto quadrato di visibilità (Fog of War). Dei **fantasmi** si nascondono nel buio e ti braccano. L'unica via è una **botola** posta lontano dalla partenza: raggiungerla significa sprofondare più giù (*Going Deeper*) e affrontare un livello più grande, con più nemici e meno visibilità. Dopo **8 livelli** il gioco finisce con un **finale tragico**.

### Loop di gioco
1. **Title screen** — sfondo 2-bit + tema musicale tragico (112 note, 3 canali, ~56 sec in loop).
2. **Gameplay** — esplorazione a griglia con camminata, **corsa** (B+direzione), **salto evasivo** (A+direzione), stamina, AI greedy multi-nemico, hitbox pixel-perfect. Indicatore `L<n>` in alto a sinistra.
3. **Game Over (Sconfitta)** — 45 frame di fermo immagine → schermata `claimed.png` + metasprite "GAME OVER" + musica tragica (128 note). START → ricomincia dallo stesso livello.
4. **Going Deeper (Vittoria, livelli 1-7)** — schermata testuale "GOING DEEPER / LEVEL N" + melodia misteriosa (96 step). START → livello successivo (più grande, più difficile).
5. **Finale (Livello 8)** — `game_over = 3`: sfondo nero, messaggio tragico (spoiler-free) + musica dedicata (192 note, lamento discendente in Re minore, loop). START → titolo.

---

## 2. Architettura del codice

### 2.1 Moduli
| File | Ruolo |
|------|-------|
| `main.c` | Entry point, loop VBL, `app_state` (0=title, 1=game). |
| `engine.c` | Orchestrazione: `title_init/update`, `engine_init`, `engine_update`, game-over branches (1/2/3). |
| `globals.c/h` | Stato globale: mappa `[21][21]`, `map_size`, `fog_radius`, `level`, `num_enemies`, enemy arrays[8], stamina, ecc. |
| `maze.c` | DFS + loop + botola. Array statici in WRAM. |
| `player_logic.c` | DAS, camminata, corsa, salto, stamina, rilevamento botola (game_over 2/3). |
| `enemy_logic.c` | AI greedy multi-entity, cooldown scalabile, rendering, hitbox. |
| `render.c` | Iso, fog scalabile, auto-tiling multi-pass, flush dinamico 16-righe, HUD stamina + livello. |
| `sound.c` | Sequencer VBL: title (112), gameplay (96), gameover (128), finale (192 loop). |
| Asset `.c` | `tiles`, `player`, `enemy`, `gameover`, `stamina`, `level`, `claimed`, `title_bg` (png2asset). |

### 2.2 Pipeline asset
Script Python (`generate_assets.py`, `generate_enemy.py`, `generate_level.py`) → PNG → `png2asset` → `src/*.c` → `lcc` (SDCC) → ROM.

---

## 3. Funzionalità chiave

### 3.1 Proiezione isometrica
```
iso_x = (lx - ly) * 2 + 12    // tile 32x16
iso_y = (lx + ly) * 1 + 2     // altezza 8px
px = (lx - ly) * 16 + 96      // pixel fisici
py = (lx + ly) * 8  + 16
```
Camera: `scroll_x = px - 64`, `scroll_y = py - 72`.

### 3.2 Generazione labirinto (`maze.c`)
- **DFS iterativo** con stack in WRAM (statico, sized per `MAX_MAP_SIZE=21`). Celle dispari = stanze, pari = muri.
- **Loop**: riapertura 15% dei muri → percorsi alternativi.
- **Botola**: cella a Chebyshev ≥ `map_size/2` da (1,1), scelta casuale.
- **Dimensioni crescenti**: `map_size = 7 + 2*(level-1)`, capped 21 (livello 8). Sempre dispari.

### 3.3 Movimento & DAS (`player_logic.c`)
- **State machine**: durante `is_moving` (16 frame, 8 in corsa) input ignorato.
- **LERP** a punto fisso `>>4`. Corsa: `move_progress += 2`.
- **DAS**: delay 12, repeat 6 (walk) / 2 (run).
- **Salto**: A+dir → 2 tile, cella intermedia deve essere muro, stamina ≥ 60. Arco parabolico visivo.
- **Corsa**: B+dir, stamina ≥ 10, 8 frame/tile, 10 stamina/tile. Fallback a walk se stamina < 10.
- **Stamina**: ricarica 1 pt ogni `stamina_recharge_rate` (60..144 frame, scala col livello).

### 3.4 Fog of War (`render.c` + `enemy_logic.c`)
Chebyshev `max(|dx|,|dy|)` con raggio `fog_radius`:
- L1-6: `fog_radius = 2` (5×5).
- L7-8: `fog_radius = 1` (3×3).
Celle a `dist == fog_radius` → tile scuro (penombra). Il nemico si attiva solo se entro `fog_radius`.

### 3.5 Auto-tiling & multi-pass
Bitmasking 4-vicini (16 varianti × 2 stili). Pass 1: pavimenti. Pass 2: botola ( Painter's algorithm). Flush **dinamico 16 righe** centrato su `center_iso_y` con wrap (2 chiamate `set_bkg_tiles` se necessario). Necessario per labirinti grandi dove la finestra fog wrappa fuori dal range fisso 2-17.

### 3.6 AI Fantasmi (`enemy_logic.c`)
- **Multi-entity**: fino a 8 fantasmi (`num_enemies = level`). Stato in array. OAM `2+i*2`.
- **Greedy**: minimizza `dx²+dy²` tra le 4 celle adiacenti. No A* (troppo pesante su 4 MHz con 8 nemici).
- **Cooldown scalabile**: `enemy_step_cooldown = 60 - 7*(level-1)` (floor 10). Sfasamento iniziale `i*8`.
- **Hitbox pixel-perfect**: `|dx|<12 && |dy|<6`.
- **Culling**: renderizzato solo se entro `fog_radius` e on-screen.

### 3.7 Audio (`sound.c`)
Sequencer via VBL interrupt, 4 canali APU:
- **Title**: 112 note, 3 canali (CH1 melodia + CH2 basso indipendente + CH4 rintocchi), ~56 sec, loop. Progressione Dm-Bb-F-C-A7-Gm-A7 con C# (7ª armonica) e discesa cromatica. Envelope haunting.
- **Gameplay**: 96 note eerie pulse, 20 frame/nota.
- **Gameover**: 128 note polifoniche + noise (thud/crash), 10 frame/nota.
- **Finale**: 192 note (24 accordi), lamento discendente Dm→abisso (C2), 14 frame/nota, **loop infinito**. CH1 melodia sommessa + CH2 basso profondo + CH4 toll (mid/crash/deep).
- **Going Deeper**: 96 note misteriose, 15 frame/nota.
- **SFX**: salto (sweep up CH1), cattura (sweep down CH1).

### 3.8 HUD
- **Stamina** (alto dx): 5 sprite OAM 18-22. Base VRAM `tiles_TILE_COUNT` (≥128, workaround overlap).
- **Livello** (alto sx): 3 sprite OAM 23-25, asset `level.png` (glifi L, 0-9). Base VRAM allineata a indice **pari** (8x16 hardware ignora LSB). `-keep_duplicate_tiles` per ordine prevedibile. Nascosto durante game over.

### 3.9 Progressione livelli
- **8 livelli** con difficoltà crescente:
  - Maze: 7×7 → 21×21 (+2/livello).
  - Nemici: 1 → 8 (+1/livello).
  - Cooldown fantasma: 60 → 11 frame.
  - Ricarica stamina: 60 → 144 frame/pt.
  - Nebbia: 5×5 → 3×3 (dal L7).
- **Sconfitta**: ricomincia dallo stesso livello (non azzera).
- **Livello 8 superato**: `game_over = 3` (finale tragico) invece di 2.

### 3.10 Schermate
- **Title**: `title_bg.png` (160×144, 2-bit) + musica.
- **Death**: `claimed.png` (160×144, 2-bit) + metasprite "GAME OVER".
- **Going Deeper**: testo font IBM "GOING DEEPER / LEVEL N" (ex immagine, sostituita per risparmiare ROM).
- **Finale**: font IBM su sfondo nero (BGP 0x1B invertito), scritta diretta in `map_buffer` (tile = ASCII-32, no printf).

---

## 4. Workaround e fix storici (dalla git history)

| Commit | Problema | Workaround |
|--------|----------|------------|
| `93deb35` | VRAM overlap stamina/BG | Load stamina a `tiles_TILE_COUNT` (≥128). |
| `6d94992` | 2-frame lag DAS | Sync DAS con state machine passo. |
| `7d85aec` | Perfect maze intrappolava | Riapertura 15% muri → loop. |
| `b47455c` | Offset rendering nemico | Wrap `&255` + hitbox pixel-perfect 12×6. |
| `f14e264` | Scale bloccavano fantasma | Ridisegnate come botola (tile 2 calpestabile). |
| `cb19677` | Glitch next_level + scroll | Reset SCX/SCY + quantizzazione soglie fisse. |
| (livelli) | ROM >32KB con 3 immagini full-screen | Sostituito next_level image con testo font; claimed image.resize per fit. |
| (HUD livello) | Base VRAM dispari in 8x16 | Allineamento a pari `(raw+1) & 0xFE`. |
| (flush) | 32-row flush stallsava 5 frame | Flush dinamico 16-righe centrato + wrap. |
| (EVELYN) | Warning SDCC 110 | Easter-egg Frank Zappa, benigno. |

---

## 5. Debiti tecnici e osservazioni

1. **`test_movement.py`**: cerca `hello_iso.noi` nella cwd ma il Makefile genera solo `test_gameover.noi` in `build/`. Script stale.
2. **Warning 110 SDCC** ("EVELYN the modified DOG"): benigno, Easter-egg di Sandeep Dutta (omaggio a Frank Zappa, canzone "Evelyn, a Modified Dog"). Indica che l'ottimizzatore ha rielaborato il flusso di controllo.
3. **`victory.c/h` orfani**: rimossi (sostituiti da `next_level`/finale).
4. **Flush 16-righe**: ~2-3 frame di stall per `draw_map` (preesistente, accettabile). draw_map chiamato solo ai passi del movimento.
5. **Sprite budget**: ~27 sprite su 40. Per-scanline (10) rispettato (HUD alto, player centro, nemici sparsi nel fog).

---

## 6. Test & verifica

Pipeline headless (PyBoy + OpenCV):
- `test_pyboy.py` / `take_screenshot.py`: screenshot della ROM.
- `test_movement.py`: legge maze in WRAM e simula input (indirizzi stale).
- `opencv_analyze_tiles.py`: rileva disallineamenti isometrici.
- `test_gameover.gb`: ROM standalone per schermata game over.
- `test_finale.gb`: ROM standalone che va subito al finale (musica + testo) per test rapidi.

Verificato via PyBoy: dimensioni 7→21, nemici 1→8, cooldown 60→11, recharge 60→144, fog 2→1 (L7), hatch L1→game_over=2 / L8→game_over=3, finale renderizza + START→title→L1, death screen claimed.png, title music 3 canali attivi.

---

## 7. Conclusione

"A Scream from the Dark" è un survival-horror completo per Game Boy: 8 livelli di difficoltà crescente, multi-nemico, corsa e salto con stamina, fog of war scalabile, audio polifonico procedurale (4 tracce + SFX), finale tragico con musica dedicata — tutto in 32 KB di ROM e ~3 KB di WRAM. Il codice è modulare, commentato in italiano, e rappresenta un caso di studio su come tradurre feature "moderne" in matematica a punto fisso e gestione diretta dei registri hardware del Game Boy.