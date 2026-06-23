# Architettura di Base

## Organizzazione del Progetto

Il progetto è strutturato in modo da separare logicamente gli asset visivi dal codice sorgente:
- `assets/`: Contiene le immagini PNG (sprite, tileset) create dagli script.
- `scripts/`: Script Python per la generazione procedurale di grafica (es. metasprite del fantasma o del game over).
- `src/`: Tutto il codice sorgente C e gli header generati.
- `build/`: Risultato della compilazione (i file `.o` e il ROM `.gb` finale).

## Modularizzazione del Codice C

Inizialmente, l'intero gioco risiedeva in un unico file `engine.c` di oltre 1000 righe. Per facilitare la manutenzione, è stato rifattorizzato in moduli a singola responsabilità:

- `maze.c`: Gestisce puramente i dati della mappa e la loro generazione.
- `sound.c`: Isola tutte le interazioni con l'hardware audio (APU).
- `render.c`: Isola l'hardware visivo (PPU), la memoria video (VRAM) e lo scrolling (SCX/SCY).
- `player_logic.c` ed `enemy_logic.c`: Contengono le regole fisiche e l'AI.
- `engine.c`: Agisce da "Direttore d'Orchestra", richiamando i vari `update` in sequenza.

## Gestione dello Stato Globale (`globals.h`)

Un problema ricorrente nei giochi C in più moduli sono le "dipendenze circolari" (es. il render ha bisogno delle coordinate del player, ma il player ha bisogno della mappa per le collisioni). 
Per risolvere questo, lo stato mutabile del gioco è centralizzato in `globals.c` ed esposto tramite `globals.h`.
Tutti i moduli includono `globals.h` e leggono/scrivono sulle variabili `extern` (come `stamina`, `game_over`, `player_lx`), evitando grovigli di include e rendendo il passaggio dei dati estremamente leggero e globale, un approccio molto comune ed efficiente nello sviluppo retro-console.
