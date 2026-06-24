# A Scream from the Dark — Report Tecnico Approfondito

> Labirinto isometrico con inseguimento per Game Boy (DMG/CGB), scritto in C con **GBDK-2020**.
> Repository: `gameboy-hello-iso` · Target ROM: `build/hello_iso.gb` (32 KB).
> ~5941 righe di C/H + ~1710 righe di script Python per la pipeline asset.

---

## 1. Identità del gioco

"A Scream from the Dark" è un piccolo survival-horror procedurale in prospettiva isometrica 2.5D. Il giocatore è imprigionato in un labirinto 7×7 generato casualmente, illuminato solo da un ristretto quadrato di visibilità (Fog of War). Un **fantasma** si nasconde nel buio e bracca il giocatore non appena entra nel suo riquadro visivo (5×5). L'unica via di fuga è una **botola** (`maze[y][x] == 2`) piazzata sul bordo sud della mappa: raggiungerla significa "sprofondare più giù" (*Going Deeper*) e avanzare di livello.

Loop di gioco:
1. **Title screen** — copertina 2-bit + tema solenne/misterioso (32 battute).
2. **Gameplay** — esplorazione a griglia con movimento interpolato, salto evasivo a consumo di stamina, AI greedy del fantasma, hitbox pixel-perfect.
3. **Game Over (Sconfitta)** — "fermo immagine" drammatico di 45 frame → schermo nero → metasprite `GAME OVER` + concerto tragico polifonico di 128 note con percussioni (noise channel).
4. **Going Deeper (Vittoria)** — reset scroll + immagine a tutto schermo `next_level.png` + melodia misteriosa discendente di 96 step. Premi START per rigenerare un nuovo livello.

---

## 2. Architettura del codice

### 2.1 Organizzazione modulare
Il progetto nasceva da un monolite `engine.c` di oltre 1000 righe, poi rifattorizzato in moduli a singola responsabilità. L'orchestrazione avviene in `main.c` / `engine.c`; lo stato mutabile è centralizzato in `globals.c`/`globals.h` per evitare dipendenze circolari tra moduli C.

| File | Ruolo |
|------|-------|
| `main.c` | Entry point, loop VBL, macchina a stati `app_state` (0=title, 1=game). |
| `engine.c` | "Direttore d'orchestra": `title_init/update`, `engine_init`, `engine_update`. |
| `globals.c/h` | Stato globale: mappa, camera, player, enemy, stamina, game_over. |
| `maze.c` | Generazione procedurale DFS + creazione loop + posizionamento botola. |
| `player_logic.c` | Input, DAS, state machine del movimento, salto, stamina. |
| `enemy_logic.c` | AI greedy, cooldown, rendering nemico, hitbox pixel-perfect. |
| `render.c` | Proiezione isometrica, fog of war, autotiling, multi-pass, stamina UI, sprite player. |
| `sound.c` | Sequencer audio via VBL interrupt, 4 tracce (title/gameplay/gameover/next_level). |
| `tiles.c/player.c/enemy.c/gameover.c/next_level.c/stamina.c/title_bg.c` | Asset generati da `png2asset`. |

### 2.2 Pipeline asset (Python → C)
`scripts/generate_assets.py` (PIL) produce `tiles.png`/`player.png` da matrici di pixel; `generate_enemy.py` genera il fantasma; `process_next_level.py` quantizza `next_level_original.png` a 4 livelli con soglie fisse. Il `Makefile` poi invoca `png2asset` per convertire ogni PNG in `src/*.c` (map, metasprite, tile data). `make clean` cancella anche i C generati, forzando la rigenerazione.

---

## 3. Funzionalità chiave in dettaglio

### 3.1 Proiezione isometrica
Conversione griglia logica `(lx,ly)` → schermo:
```
iso_x = (lx - ly) * 2 + 12   // tile 32x16 → metà larghezza
iso_y = (lx + ly) * 1 + 2    // tile altezza 8px logica
```
Coordinate fisiche pixel del player/nemico usate per camera & collision:
```
px = (lx - ly) * 16 + 96
py = (lx + ly) * 8  + 16
```
Camera centrata: `scroll_x = px - 64`, `scroll_y = py - 72` (160×144 display → centro 80×72, con offset hardware).

### 3.2 Generazione del labirinto (`maze.c`)
- **DFS iterativo con stack in WRAM** (`stack_x/y` statici, sized `(MAX_MAP_SIZE/2)^2`): evita l'overflow dello stack hardware del LR35902. Celle dispari = stanze, celle pari = muri divisori; scava il muro di mezzo con la media aritmetica delle coordinate.
- **Dimensione crescente col livello**: `map_size = MAP_SIZE + 2*(level-1)`, capped a `MAX_MAP_SIZE`=21 (raggiunto al livello 8, sempre dispari). L'array `maze` è allocato `[MAX_MAP_SIZE][MAX_MAP_SIZE]` (441 byte) e i moduli usano `map_size` come bound runtime.
- **Fase 2 — loop**: riapre muri residui che collegano due corridoi opposti con probabilità 15%. Vitale per il gameplay d'inseguimento.
- **Fase 3 — botola**: sceglie una cella calpestabile a distanza di Chebyshev ≥ `map_size/2` dalla partenza `(1,1)` (soglia scalata: 3 per 7x7, 8 per 17x17), tra **tutte** le celle del labirinto. Fallback sulla cella più lontana in assoluto.

### 3.3 Movimento & DAS (`player_logic.c`)
- **State machine rigida**: durante `is_moving` (16 frame di LERP, o 8 in corsa) ogni input è ignorato → movimento strettamente grid-based stile Zelda/Pokémon.
- **LERP** a punto fisso: `px = start_px + ((target_px - start_px) * move_progress) >> 4`. In corsa `move_progress` incrementa di 2/frame → il passo dura 8 frame invece di 16.
- **DAS (Delayed Auto Shift)** alla Tetris: `DAS_DELAY=12` frame di attesa iniziale, poi `DAS_REPEAT=6` frame tra ripetizioni (camminata); `DAS_REPEAT_RUN=2` mentre si corre per incatenare i tile.
- **Salto evasivo**: A+direzione → atterraggio 2 tile più in là. Condizioni: cella intermedia DEVE essere muro, cella di arrivo pavimento/vittoria, stamina ≥ 60. Consuma 60 stamina. Arco parabolico solo visivo: `y_offset = (move_progress * (16 - move_progress)) >> 2`.
- **Corsa**: B+direzione (stamina ≥ 10) → passo di 8 frame, costo 10 stamina/tile, DAS rapido. Se stamina < 10 ripiega su camminata normale senza costo.
- **Stamina**: ricarica 1 punto/s. Barra UI a 5 sprite (ID 18–22) in alto a destra.

### 3.3b Progressione livelli (`globals.c` + `engine.c` + `render.c`)
- Variabile globale `level` (parte da 1). Il titolo→gioco la azzera a 1 (`main.c`); raggiungere la botola (vittoria, `game_over==2`) e premere START fa `level++` prima di `engine_init()` (nuovo labirinto); la sconfitta (`game_over==1`) + START **non azzera** il livello: si ricomincia dall'ultimo raggiunto (nuova mappa, stesso `level`).
- Indicatore HUD `L<n>` in alto a sinistra via 3 sprite (OAM ID 23–25), disegnati dall'asset `level.png` (11 glifi 8x16: 'L', '0'–'9') generato da `scripts/generate_level.py` e convertito con `png2asset -keep_duplicate_tiles` (senza deduplica, così il glifo di ordine i occupa i tile 2i/2i+1 in ordine prevedibile).
- **VRAM**: i glifi sono caricati a `LEVEL_SPRITE_BASE = allineamento-pari-di (tiles_TILE_COUNT + stamina_TILE_COUNT*2)` (~204) — base PARI perché in modalità 8x16 l'hardware ignora il LSB dell'indice tile; e disgiunta dal blocco tile del background e dalla stamina (stesso workaround del commit 93deb35). `update_level_display()` viene chiamata ogni frame in `engine_update` e si nasconde da sola quando `game_over` è attivo.

### 3.4 Fog of War (`render.c` + `enemy_logic.c`)
Distanza di **Chebyshev** `max(|dx|,|dy|)` invece di euclidea (no sqrt, no lookup): quadrato di visibilità 5×5.
- `dist > 2` → cella non disegnata (nera).
- `dist == 2` → offset grafico scuro ("Tile Dark") per simulare affievolimento della luce prima del buio.
- Il nemico si "sveglia" e insegue solo se `dist <= 2` (entra nel cono visivo): coerente con la nebbia.

### 3.5 Autotiling & multi-pass rendering
- **Maschera a 4 bit** sui vicini (TL, TR, BL, BR) per scegliere varianti di bordo/angolo (16 varianti × 2 stili di pavimento alternati a scacchiera `is_alt = (lx+ly)%2==0`).
- **Problema overlapping isometrico**: il background GB non ha trasparenza hardware; i tile disegnati dopo "tagliano" quelli prima con angoli piatti. Soluzione ibrida:
  1. **Pass 1**: pavimenti normali con bitmasking dinamico degli angoli (ricolorano in base al vicino).
  2. **Pass 2**: la botola (oggetto complessa, 243+81+162 varianti con maschera a 4 vicini `state_tl + state_tr*3 + state_bl*9 + state_br*27`) disegnata **per ultima**, sovrascrive i pavimenti frontali ma si fonde grazie alle maschere dei propri angoli inferiori.
- Questo evita l'uso di sprite hardware per la botola (che causerebbero flickering per il limite di 10 sprite/scanline) e contiene il consumo di VRAM (limite 256 tile).

### 3.6 Ottimizzazione rendering
`memset` azzera `map_buffer` (32x32) ad ogni `draw_map`, poi disegna solo la finestra fog (2r+1)^2. Flush **dinamico a 16 righe** (512 byte) centrato sulla iso_y del centro di disegno, con gestione del wrap della mappa 32x32 via due `set_bkg_tiles` quando la finestra attraversa il bordo. Necessario perché con labirinti grandi la nebbia, in coordinate iso assolute, wrappa fuori dal vecchio range fisso 2-17; 16 righe mantengono le prestazioni originali. Aggiornamento a `move_progress==8` (metà passo) per fluidità del fog of war.

### 3.7 AI dei fantasmi (`enemy_logic.c`) — multi-entity
- **Fino a 8 fantasmi** (`num_enemies = level`, capped `MAX_ENEMIES=8`): stato in array indicizzati (`enemy_lx[i]`, `enemy_is_moving[i]`, ...). Ogni fantasma usa 2 slot OAM a partire da `2 + i*2` (il player usa 0-1).
- **Greedy invece di A***: per ciascun fantasma, tra le 4 celle adiacenti calpestabili sceglie quella che minimizza la distanza al quadrato verso il giocatore (no sqrt, no heap). Difetto voluto: si incastra nei vicoli a U.
- **Cooldown scalabile**: dopo ogni passo (16 frame LERP) il fantasma aspetta `enemy_step_cooldown` frame (60 al L1, ~11 al L8). Cooldown iniziali sfasati (i*8) per non sincronizzarli.
- **Attivazione**: insegue solo se entro il raggio di nebbia (Chebyshev ≤ `fog_radius`).
- **Hitbox pixel-perfect**: la morte scatta se i pixel di un qualunque fantasma si sovrappongono a quelli del giocatore (|dx|<12, |dy|<6); al primo catch il loop si ferma (`return`).
- **Culling**: `enemy_screen_x/y` con wrap `& 255` + soglie fisiche; fuori range o oltre la nebbia lo sprite va offscreen.

### 3.8 Audio (`sound.c`)
Sequencer agganciato al **VBL interrupt** (`add_VBL(play_music_tick)`), ~60 Hz, non blocca il rendering. Usa i 4 canali APU:
- **CH1** (pulse+sweep): arpeggi rapidi (gameover/next_level), tema title.
- **CH2** (pulse): bassi/melodie tenute (gameover ch2_seq, basso title/next_level un'ottava sotto con `n/2`).
- **CH4** (noise): percussioni — `step%8==0` trigger; freq `0x68` (thud basso) per `step<64`, `0x42` (crash) per `step>=64`.
- **CH3** (wave): non utilizzato.

Tracce:
- **Title**: `title_melody[32]`, 30 frame/nota, basso ogni 4 step, accordi Am–G–F–E.
- **Gameplay**: `eerie_reg_vals[96]`, 20 frame/nota, pattern A min–D min–E7 (ansia crescente).
- **Game Over**: `ch1_seq[128]` + `ch2_seq[128]`, 10 frame/nota, 16 accordi con intensificazione (arpeggi più alti nella seconda metà).
- **Going Deeper**: `next_level_seq[96]`, 15 frame/nota, 6 sezioni (Am, Fmaj7, Dm, E7, C aug, discesa finale nel buio `N_G2 N_E3 N_C3… N_C2 R…`).

Frequenze delle note: costanti `N_*` precalcolate come `(2048 - 131072/freq)` → scritte direttamente in `NR13/NR23` (low) e `NR14/NR24` (high | 0x80 trigger).

---

## 4. Workaround e fix storici (dalla git history)

La cronologia di 23 commit racconta un'intensa fase di caccia ai bug hardware-specifici del Game Boy. Riepilogo dei workaround più significativi:

| Commit | Problema | Workaround |
|--------|----------|------------|
| `93deb35` | **VRAM shared memory overlap**: i tile della stamina UI (sprite) sovrascrivevano i tile del background perché caricati nello stesso blocco VRAM. | Caricare `stamina_tiles` **dopo** i background tile e a partire da `tiles_TILE_COUNT` (indici ≥128, fuori dal blocco condiviso). `base_tile = tiles_TILE_COUNT` in `update_stamina_display`. |
| `6d94992` | **2-frame lag tra tile**: il DAS non era sincronizzato col ciclo di movimento. | Sincronizzazione del timer DAS con la state machine del passo. |
| `7d85aec` | Labirinto "perfetto" intrappolava il giocatore. | Fase 2: riapertura casuale 15% dei muri → loop evasivi. |
| `b47455c` | Offset rendering nemico errato + collisione approssimata. | Calcolo `screen_x = ((px - scroll) & 255) + 24/+16` e hitbox pixel-perfect 12×6. |
| `c983631` | Palette sprite errata per il nemico su DMG + game over troppo brusco. | `OBP1_REG = 0x1B` (palette invertita per fantasma bianco) + `game_over_timer` di delay. |
| `e07e8c6` | Nemico invisibile fuori schermo a causa dello scroll. | Wrap `& 255` + culling con soglie fisiche. |
| `8d71a23` / `1b0e1a0` | Artefatti sprite sulle scale. | Primo tentativo sprite-based con `-spr8x16`, poi **revert** a tile-based (le scale tornano nel background). |
| `f14e264` | Scale come ostacolo bloccava il fantasma. | Ridisegno come **botola nel terreno**: il fantasma può camminarci sopra (tile 2 è calpestabile per l'AI: `maze[ly][lx] != 0`). |
| `cb19677` | Glitch immagine next_level + scroll non allineato. | Reset `SCX_REG=SCY_REG=0` prima di mostrare l'immagine a tutto schermo + miglioramento quantizzazione colore. |
| `d8fd746` | Quantizzazione dell'immagine perdeva i toni scuri. | Soglie fisse in `process_next_level.py`: `<40` nero, `40–128` grigio scuro (85), `128–200` grigio chiaro (170), `≥200` bianco. |
| `cc656d0` | Musica next_level poco udibile + fine brusco. | Envelope più alto (`NR12_REG=0xC5`) e discesa graduale fino a `N_C2 R…`. |

**Pattern ricorrente di workaround GB**: ogni "feature" ha dovuto litigare con i limiti hardware — VRAM da 256 tile condivisa tra BG e sprite, assenza di trasparenza nel background, limite 10 sprite/scanline, CPU 4 MHz senza FPU, stack da 8 bit. La filosofia è **"ingannare l'hardware con la matematica"**: LERP a punto fisso, distanze al quadrato/Chebyshev, multi-pass con bitmasking, sequencer audio via interrupt.

---

## 5. Test & verifica headless

Pipeline di verifica senza emulatore grafico (PyBoy + OpenCV):
1. **`test_pyboy.py` / `take_screenshot.py`**: avvia la ROM in PyBoy per N frame e salva screenshot (`hello_iso_gb.png`).
2. **`test_movement.py`**: legge la griglia maze in WRAM (indirizzo cercato dinamicamente via `hello_iso.noi`) e simula pressioni direzionali, verificando `player_lx/ly`. Nota: lo script cerca `hello_iso.noi` ma il Makefile produce `test_gameover.noi` in `build/` — potenziale incongruenza di percorso (vedi §7).
3. **`opencv_analyze_tiles.py` / `opencv_check_centering.py`**: rilevano disallineamenti/buchi neri tra giunzioni isometriche e centratura.
4. **`test_gameover_render.c`** + target `test_gameover.gb`: ROM standalone che renderizza solo player + metasprite GAME OVER per validare visivamente la schermata di sconfitta isolata.

---

## 6. Punti di forza tecnici

- **Modularizzazione pulita** con stato centralizzato: leggibile e manutenibile nonostante i vincoli embedded.
- **Commenti didattici** in italiano: ogni modulo spiega il *perché* delle scelte (es. "non usiamo sqrt perché troppo costosa"), utile come materiale di studio GB dev.
- **Niente float**: tutto a punto fisso con shift (`>> 4`, `>> 2`), essenziale sul LR35902.
- **Audio interamente procedurale**: nessun campione, solo registri APU; la ROM resta compatta (32 KB).
- **Pipeline asset riproducibile**: `make clean && make` rigenera tutto da PNG sorgenti.

---

## 7. Incongruenze, debiti tecnici e osservazioni

1. **README obsoleto**: il `README.md` storico parlava di "gioco carino", titoli `file:///home/enne2/dev/gameboy-hello/iso_test/...` (percorso storico diverso da quello attuale `gameboy-hello-iso`) e non menzionava "A Scream from the Dark", né il salto/stamina/fantasma/botola. Risolto in questa revisione allineando il README all'identità attuale.
2. **`doc/generation.md` vs `maze.c`**: la doc descriveva il posizionamento del traguardo via **distanza di Manhattan massima**; il codice attuale sceglie invece un **punto casuale sul bordo sud**. Risolto in questa revisione aggiornando `doc/generation.md`.
3. **`victory.c/h` orfani**: l'asset `victory` (scritta VITTORIA) era ancora compilato e incluso da `render.c` ma la sequenza di vittoria è stata sostituita dall'immagine a tutto schermo `next_level` (commit `3aa20fd`). Risolto in questa revisione rimuovendo l'inclusione e i file morti.
4. **`test_movement.py`**: cerca `hello_iso.noi` nella cwd, ma il `.noi` viene generato in `build/` (per `test_gameover`); per la ROM principale il `.noi` non è tra i target Makefile espliciti. Lo script può fallire se eseguito fuori da `build/`. (Osservazione residua, non bloccante.)
5. **`game_over` come `volatile`**: marcato `volatile` in `globals.h` (corretto, modificato da ISR audio/VBL), ma alcuni aggiornamenti avvengono anche dal main loop non-atomic — in pratica sicuro perché la lettura/scrittura è a 8 bit sul LR35902 (atomica), ma vale la pena documentarlo.
6. **`app_state` ridefinito** in `globals.h` e `engine.h` (entrambi `extern uint8_t app_state`): duplicazione inoffensiva ma ridondante.
7. **Spawn player fallback**: ricerca la prima cella libera se `(1,1)` è muro (teoricamente impossibile col DFS partendo da 1,1) — difensivo, buon codice.
8. **`title_update` vuoto**: il loop del titolo non fa nulla a parte il polling (gestito in `main.c`). La musica continua via interrupt. Pulito ma il corpo vuoto andrebbe commentato o rimosso se non serve estensione futura.
9. **Costante `N_E2 = 458`** in `next_level_seq` mentre le altre note `N_*2` sono nell'ordine di 44–961: c'è un salto numerico marcato. `N_C2=44` è la nota più grave (registro APU = 44 → freq ~131 Hz, Do2). `N_E2=458` non segue la formula `2048-131072/f` in modo coerente con gli altri `N_*2` (es. `N_D2` non è definito): vale la pena verificare che la discesa finale `N_G2 N_E3 N_C3 … N_E2 N_C3 N_G2 … N_C2` suoni effettivamente come inteso. Sospetto di coerenza tonale da validare all'ascolto.

---

## 8. Mappa mentale del flusso runtime

```
main.loop (VBL-synced)
 ├─ app_state==0 → title_update (no-op)        [musica: VBL interrupt → play_music_tick]
 │  └─ J_START fronte → engine_init()
 └─ app_state==1 → engine_update
     ├─ if game_over:
     │    ├─ game_over_timer>0 → countdown; a 0: svuota BG (sconfitta) o mostra next_level (vittoria)
     │    ├─ timer==0 → metasprite GAME OVER + player + (enemy se vicino) 
     │    └─ J_START → engine_init() (riavvio)
     ├─ update_enemy_logic()   [AI greedy, cooldown, hitbox → game_over=1]
     └─ update_player_movement [DAS, LERP, salto, stamina, vittoria → game_over=2]
        └─ durante is_moving: scroll/move_bkg + draw_map a frame 8 + sprite
```

---

## 9. Conclusione

"A Scream from the Dark" è un piccolo gioiello di ingegneria embedded: realizza proiezione isometrica, generazione procedurale, AI di inseguimento, audio polifonico e un'interfaccia stamina — tutto nei 32 KB e 8 KB WRAM di un Game Boy del 1989. Il valore didattico è alto: ogni modulo è un caso di studio su come **tradurre feature "moderne" in matematica a punto fisso e gestione diretta dei registri hardware**. Le incongruenze principali erano cosmetiche (README/doc da allineare all'identità attuale, asset `victory` orfano) e non intaccavano la correttezza; sono state risolte in questa revisione. Il codice è in ottima forma per essere esteso (più livelli con difficoltà crescente, nuovi nemici, oggetti raccoglibili) o usato come base per tutorial di sviluppo GB.