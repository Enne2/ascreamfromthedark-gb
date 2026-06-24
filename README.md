# A Scream from the Dark

Un survival-horror procedurale in prospettiva isometrica per Game Boy (DMG/CGB), scritto in C con **GBDK-2020**. Sei imprigionato in un labirinto 7×7 generato casualmente, illuminato solo da un ristretto quadrato di visibilità. Un **fantasma** si nasconde nel buio e ti bracca non appena entri nel suo raggio visivo. L'unica via di fuga è la **botola** sul bordo sud della mappa: raggiungerla significa "sprofondare più giù" (*Going Deeper*) e generare un nuovo livello.

---

## 🎮 Caratteristiche

- **Proiezione isometrica 2.5D**: rendering della mappa a diamante (tile 32×16 px) su schermo Game Boy, con autotiling dinamico.
- **Labirinto casuale**: algoritmo DFS iterativo con stack in WRAM (per evitare overflow dello stack hardware) che genera un "perfect maze" 7×7 unico ad ogni partita, poi "rotto" con riaperture casuali al 15% per creare loop e percorsi alternativi.
- **Fog of War**: visibilità 5×5 basata sulla distanza di Chebyshev, con affievolimento della luce sui bordi. Il fantasma si attiva solo quando entra in questo riquadro.
- **Movimento interpolato (LERP)**: spostamenti fluidi del personaggio e della telecamera su 16 tick a punto fisso (no float).
- **Delayed Auto-Shift (DAS)**: controlli alla Tetris — delay iniziale di 12 frame e ripetizione ogni 6 frame per il movimento continuo tenendo premuto il D-Pad.
- **Salto evasivo con Stamina**: A+direzione scavalca il blocco adiacente atterrando 2 tile più in là (la cella intermedia deve essere un muro). Costa 60 punti stamina; la barra si ricarica di 1 punto al secondo.
- **Corsa con Stamina**: B+direzione fa correre il protagonista: il passo dura 8 frame invece di 16 e consuma 10 stamina per tile, con DAS più rapido per incatenare i tile fluidamente. Se la stamina scende sotto 10 ripiega automaticamente sulla camminata normale.
- **Progressione livelli**: si parte dal livello 1; raggiungere la botola fa sprofondare nel livello successivo (livello +1). L'indicatore `L<n>` in alto a sinistra (sprite HUD, come la barra stamina in alto a destra) mostra il livello corrente e si aggiorna ad ogni livello superato. In caso di sconfitta si ricomincia dall'**ultimo livello raggiunto** (il contatore non si azzera).
- **AI del fantasma**: pathfinding greedy con distanza al quadrato (niente sqrt, niente A*), cooldown di 1 secondo tra i passi, hitbox pixel-perfect (12×6 px) per una morte "giusta".
- **Audio procedurale**: colonna sonora sintetizzata manipolando direttamente i registri APU via VBL interrupt (nessun campione).
- **Schermate a tutto schermo**: copertina 2-bit nativa per il titolo, immagine "Going Deeper" per la vittoria, metasprite "GAME OVER" per la sconfitta.
- **Test headless**: pipeline di verifica con PyBoy + OpenCV senza emulatore grafico.

### Soundtrack

1. **Title Theme**: solenne e misteriosa, 32 battute sugli accordi La minore, Sol, Fa e Mi.
2. **Gameplay Theme**: battito ritmico ansioso ("eerie pulse") che accelera la tensione dell'inseguimento.
3. **Game Over Theme**: concerto tragico polifonico di 128 note con percussioni (noise channel), basso virtuoso e drammatica discesa melodica.
4. **Going Deeper**: melodia misteriosa discendente di 96 step (Am → Fmaj7 → Dm → E7 → C aug → abisso).

---

## 🛠️ Dettagli tecnici

### Architettura dei file
- [`main.c`](src/main.c): entry point, loop VBL sincronizzato, macchina a stati `app_state` (0 = title, 1 = game).
- [`engine.c`](src/engine.c) / [`engine.h`](src/engine.h): "direttore d'orchestra" — `title_init/update`, `engine_init`, `engine_update`.
- [`globals.c`](src/globals.c) / [`globals.h`](src/globals.h): stato globale centralizzato (mappa, camera, player, enemy, stamina, `game_over`) per evitare dipendenze circolari tra moduli.
- [`maze.c`](src/maze.c): generazione procedurale DFS + loop + posizionamento botola.
- [`player_logic.c`](src/player_logic.c): input, DAS, state machine del movimento, salto, stamina.
- [`enemy_logic.c`](src/enemy_logic.c): AI greedy, cooldown, rendering nemico, hitbox pixel-perfect.
- [`render.c`](src/render.c): proiezione isometrica, fog of war, autotiling multi-pass, stamina UI, sprite player.
- [`sound.c`](src/sound.c): sequencer audio via VBL interrupt, 4 tracce.
- `tiles.c / player.c / enemy.c / gameover.c / next_level.c / stamina.c / title_bg.c`: asset generati da `png2asset`.
- [`scripts/`](scripts/): generazione procedurale di tile/sprite (`generate_assets.py`, `generate_enemy.py`), quantizzazione immagini (`process_next_level.py`), test headless.

### Formato delle coordinate isometriche
Le coordinate logiche `(lx, ly)` vengono convertite in coordinate schermo `(iso_x, iso_y)`:
```
iso_x = (lx - ly) * 2 + 12
iso_y = (lx + ly) * 1 + 2
```
e in coordinate pixel fisiche per camera/collisione:
```
px = (lx - ly) * 16 + 96
py = (lx + ly) * 8  + 16
```
Camera centrata: `scroll_x = px - 64`, `scroll_y = py - 72`.

Per un'analisi approfondita di codice, funzionalità e workaround storici, vedi [`doc/AScreamFromTheDark_report.md`](doc/AScreamFromTheDark_report.md).

---

## 🚀 Requisiti e build

### Prerequisiti
1. **GBDK-2020** installato in `/home/enne2/.local/gbdk`.
2. **Python 3** con i pacchetti per la rigenerazione degli asset e i test:
   ```bash
   pip install --user Pillow pyboy opencv-python numpy
   ```

### Compilazione
```bash
make clean && make
```
Questo comando:
1. Esegue gli script Python per creare `tiles.png`, `player.png`, `enemy.png`.
2. Usa `png2asset` per convertire i PNG in sorgenti C.
3. Usa il compilatore `lcc` di GBDK per compilare e linkare i sorgenti in `build/hello_iso.gb` (e `build/test_gameover.gb`).

---

## 🧪 Test e analisi automatica

1. **Screenshot** — `python3 scripts/test_pyboy.py`: avvia la ROM in PyBoy per 120 frame e salva `assets/hello_iso_gb.png`.
2. **Test di movimento in WRAM** — `python3 scripts/test_movement.py`: legge la griglia del labirinto in WRAM (indirizzo risolto dinamicamente via `hello_iso.noi`) e simula pressioni direzionali verificando `player_lx/ly`.
3. **Rilevamento glitch con OpenCV** — `python3 scripts/opencv_analyze_tiles.py`: esamina lo screenshot cercando disallineamenti o buchi neri tra le giunzioni isometriche.
4. **ROM di test isolata** — `make build/test_gameover.gb`: renderizza solo player + metasprite GAME OVER per validare la schermata di sconfitta.

La documentazione tecnica dettagliata per modulo è in [`doc/`](doc/).