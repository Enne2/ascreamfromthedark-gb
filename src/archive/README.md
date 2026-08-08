# Moduli archiviati (non compilati)

Moduli C non referenziati dalla build (`Makefile` → `SRCS`), conservati per
consultazione o eventuale ripristino. **Non fanno parte della ROM.**

- `final_victory.c/h` — asset `png2asset` per una schermata di vittoria finale
  (`final_victory.png`, ora in `assets/wip/`). Il gioco usa invece il finale
  tragico in `src/screens/finale.c`.
- `level_ui.c/h` — asset `png2asset` per la UI di livello (`level_ui.png`, ora
  in `assets/wip/`). La UI `L<n>` corrente è renderizzata da `src/render.c`
  usando `level.png`.
- `test_stairs_connect.c`, `test_going_deeper.c` — ROM di test sperimentali
  non più invocate dal Makefile. I test supportati sono `make test` e le ROM
  `test_gameover.gb` / `test_finale.gb`.

Per ripristinare un modulo: spostarlo in `src/` e aggiungerlo a `SRCS` nel
Makefile (e rigenerare l'asset PNG corrispondente da `assets/wip/`).
