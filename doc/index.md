# A Scream from the Dark — Documentazione Tecnica

Benvenuto nella documentazione tecnica di **A Scream from the Dark**, un survival-horror procedurale in prospettiva isometrica 2.5D per Game Boy (DMG/CGB). Il gioco è scritto in C con **GBDK-2020** (compilatore **SDCC**) e dimostra come tecniche avanzate — prospettiva isometrica, fog of war dinamico, generazione procedurale, AI multi-nemico, audio polifonico e progressione di difficoltà — possano essere implementate sulle ristrette risorse hardware del Game Boy (CPU Sharp LR35902 a 4.19 MHz, 8 KB WRAM, 32 KB ROM).

## Il gioco in breve

Sei imprigionato in un labirinto generato casualmente, illuminato solo da un ristretto quadrato di visibilità. Un **fantasma** si nasconde nel buio e ti bracca. L'unica via di fuga è una **botola** posta lontano dalla partenza: raggiungerla significa sprofondare più giù (*Going Deeper*) e affrontare un livello più grande e più difficile. Dopo **8 livelli** il gioco finisce con un **finale tragico**.

## Indice dei Capitoli

1. **[Architettura di Base](architecture.md)** — Struttura del codice, moduli, stato globale, pipeline asset, vincoli hardware.

2. **[Motore Grafico e Rendering](graphics.md)** — Proiezione isometrica, auto-tiling multi-pass, fog of war scalabile, flush dinamico, VRAM management.

3. **[Generazione Procedurale del Livello](generation.md)** — DFS con stack WRAM, creazione di loop, posizionamento della botola, dimensioni crescenti.

4. **[Fisica e Controlli del Giocatore](gameplay.md)** — DAS, state machine, camminata, corsa (B+direzione), salto evasivo, stamina, progressione livelli, finale tragico.

5. **[Intelligenza Artificiale (Fantasmi)](ai.md)** — Multi-entity (fino a 8 fantasmi), pathfinding greedy, cooldown scalabile, hitbox pixel-perfect.

6. **[Sintesi Audio e Musica](audio.md)** — 4 canali APU, sequencer via VBL interrupt, title music (112 note, 3 canali), gameplay eerie, gameover, finale dedicato (192 note, loop).

7. **[Report Tecnico Approfondito](AScreamFromTheDark_report.md)** — Analisi completa di architettura, funzionalità, workaround storici e debiti tecnici.