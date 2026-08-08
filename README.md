# A Scream from the Dark

<p align="center">
  <img src="assets/title_bg.png" alt="Title screen" width="320">
</p>

Un survival-horror procedurale in prospettiva isometrica per Game Boy (DMG/CGB), scritto in C con **GBDK-2020**. Sei imprigionato in un labirinto generato casualmente, illuminato solo da un ristretto quadrato di visibilità. Dei **fantasmi** si nascondono nel buio e ti braccano. L'unica via di fuga è una **botola** posta lontano dalla partenza: raggiungerla significa "sprofondare più giù" (*Going Deeper*) e affrontare un livello più grande, con più nemici e meno visibilità.

---

## Autore

**Matteo Benedetto** — [me@enne2.net](mailto:me@enne2.net)

Crediti visibili anche nel gioco: schermata **SELECT** dal menu titolo.

---

## Caratteristiche

- **Proiezione isometrica 2.5D**: rendering a diamante (tile 32×16 px) con autotiling dinamico e multi-pass.
- **Labirinto casuale crescente**: DFS iterativo con stack in WRAM che genera un perfect maze, rotto al 15% per creare loop. La dimensione cresce di 2 tile/lato per livello: 7×7 → 21×21.
- **Fog of War scalabile**: visibilità basata su Chebyshev. 5×5 (livelli 1-6), 3×3 (livelli 7-8). Il nemico si attiva solo quando entra nella nebbia.
- **Movimento interpolato (LERP)**: punto fisso `>>4`, no float. 16 frame/passo (8 in corsa).
- **DAS**: controlli alla Tetris — delay 12 frame, repeat 6 (walk) / 2 (run).
- **Salto evasivo**: A+direzione, 2 tile, costa 60 stamina (salto sicuro). Sotto 60 stamina il salto è rischioso: probabilità di caduta nel vuoto proporzionale alla stamina mancante. Arco parabolico visivo.
- **Corsa**: B+direzione, 8 frame/tile, 10 stamina/tile. Fallback a camminata se stamina < 10.
- **Progressione a livelli crescenti**: difficoltà crescente (maze, nemici, cooldown, stamina, nebbia). Indicatore `L<n>` in alto a sinistra. Sconfitta → ricomincia dallo stesso livello.
- **Multi-nemico**: fino a 8 fantasmi (1 per livello). AI greedy, cooldown scalabile (60→11 frame), hitbox pixel-perfect.
- **Audio procedurale**: 4 canali APU via VBL interrupt. Title (128 note, 3 canali), gameplay (96), gameover (128), finale dedicato (192, loop).
- **Schermate**: title con sfondo 2-bit, death testuale con font IBM, Going Deeper testuale, finale con font IBM.
- **Test headless**: PyBoy + OpenCV + ROM di test isolate.

### Soundtrack

1. **Title Theme**: 128 note su 3 canali (melodia + basso indipendente + kick/hi-hat noise), ~17 sec in loop. Arpeggi di inseguimento in Re minore con salita cromatica e climax.
2. **Gameplay Theme**: battito ritmico ansioso ("eerie pulse") in La minore → Re minore → Mi7.
3. **Game Over Theme**: concerto tragico polifonico di 128 note con percussioni (thud + crash).
4. **Finale**: 192 note (24 accordi), lamento discendente Dm → abisso (C2), loop infinito. CH1 melodia sommessa + CH2 basso profondo + CH4 toll (mid/crash/deep).
5. **Going Deeper**: melodia misteriosa discendente di 96 step (~24 s, Am → Fmaj7 → Dm → E7 → C aug → abisso).

---

## Dettagli tecnici

### Architettura dei file
- [`main.c`](src/main.c): entry point, loop VBL, `app_state` (0=title, 1=game).
- [`engine.c`](src/engine.c): orchestrazione, game-over branches (sconfitta/vittoria).
- [`globals.c`](src/globals.c) / [`globals.h`](src/globals.h): stato globale (mappa `[21][21]`, `map_size`, `fog_radius`, `level`, `num_enemies`, enemy arrays[8], stamina, ecc.).
- [`maze.c`](src/maze.c): DFS + loop + botola. Array statici in WRAM.
- [`player_logic.c`](src/player_logic.c): DAS, camminata, corsa, salto, stamina.
- [`enemy_logic.c`](src/enemy_logic.c): AI greedy multi-entity, cooldown scalabile, hitbox.
- [`render.c`](src/render.c): iso, fog scalabile, auto-tiling, flush dinamico, HUD.
- [`sound.c`](src/sound.c): sequencer VBL, 5 tracce + SFX.
- Asset: `tiles.c`, `player.c`, `enemy.c`, `gameover.c`, `stamina.c`, `level.c`, `title_bg.c` (generati da `png2asset`).
- [`scripts/`](scripts/): generazione asset (`generate_assets.py`, `generate_enemy.py`, `generate_level.py`, `generate_tiling_parts.py`), test (`validate_*.py`). Gli script non usati dalla build sono in `scripts/legacy/`.
- `assets/`: solo gli 8 PNG sorgente della build; scarti in `assets/wip/` (ignorato da git), materiale cartuccia in `assets/cartridge/`.
- `src/archive/`: moduli C non compilati (asset sperimentali e test orfani).

### Coordinate isometriche
```
iso_x = (lx - ly) * 2 + 12    iso_y = (lx + ly) + 2
px = (lx - ly) * 16 + 96      py = (lx + ly) * 8 + 16
```
Camera: `scroll_x = px - 64`, `scroll_y = py - 72`.

Documentazione approfondita: [`docs/`](docs/) — [index](docs/index.md), [report](docs/AScreamFromTheDark_report.md).
Sito documentazione (MkDocs): `mkdocs serve` in locale, deploy automatico su GitHub Pages via `.github/workflows/mkdocs.yml`.

---

## Requisiti e build

### Prerequisiti
1. **GBDK-2020** in `$HOME/.local/gbdk`, oppure impostare `GBDK_HOME`.
2. **Python 3** con: `pip install --user Pillow pyboy`

### Compilazione
```bash
make clean && make
```
Output: `build/hello_iso.gb` (32 KB) + `build/test_gameover.gb`.

Puoi rinominare il ROM principale con `make release`:
```bash
make release
# Crea build/"AScreamFromTheDark.gb"
```

---

## Test

1. **Suite headless deterministica** — `make test`
2. **ROM game over** — `make build/test_gameover.gb`
3. **ROM finale** — `make build/test_finale.gb` (va subito al finale con musica, per test rapidi)

La build normale usa gli asset C versionati e non modifica il working tree.
La rigenerazione esplicita da PNG si esegue con `make assets`.
