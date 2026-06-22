# gioco carino (Cute Isometric Game Boy Maze)

Un motore isometrico sperimentale per Game Boy (DMG/CGB) scritto in C con **GBDK-2020**. Genera un labirinto casuale ed esegue il rendering in proiezione isometrica con autotiling dinamico, movimento interpolato del personaggio, e un set di test automatizzati headless tramite l'emulatore **PyBoy** ed elaborazione d'immagine con **OpenCV**.

---

## 🎮 Caratteristiche Principali

*   **Proiezione Isometrica**: Rendering di una mappa 2.5D su schermo Game Boy (tile 32x16 pixel disegnate a diamante).
*   **Labirinto Casuale Dinamico**: Algoritmo di backtracking iterativo (con stack in WRAM per evitare l'overflow dello stack hardware) che genera ogni volta un percorso 7x7 unico.
*   **Movimento Interpolato (Lerp)**: Spostamenti fluidi del personaggio e della telecamera interpolati linearmente su 16 tick macchina.
*   **Delayed Auto Shift (DAS)**: Controlli reattivi e confortevoli con delay iniziale di 12 frame e ripetizione ogni 6 frame per il movimento continuo tenendo premuto il D-Pad.
*   **Autotiling Intelligente**: Calcolo dei vicini (maschera a 4 bit) per selezionare automaticamente il bordo e gli angoli di ciascuna tessera del pavimento (16 varianti per ognuno dei 2 stili di pavimento alternati a scacchiera).
*   **Pipeline di Asset Ottimizzata**: Generazione procedurale di tile e sprite da script Python (`generate_assets.py`) e compilazione in C tramite `png2asset`.
*   **Test Headless & Computer Vision**:
    *   Simulazione dell'input e verifica dello stato direttamente leggendo i registri WRAM del Game Boy in esecuzione.
    *   Rilevamento di glitch grafici (pixel neri o spazi vuoti non allineati) sulla ROM renderizzata usando filtri morfologici di **OpenCV**.

---

## 🛠️ Dettagli Tecnici

### Architettura dei File
*   [main.c](file:///home/enne2/dev/gameboy-hello/iso_test/main.c): Punto di ingresso del gioco. Esegue l'inizializzazione del ciclo macchina e del joypad e si sincronizza con l'intervallo di VBlank (`wait_vbl_done()`).
*   [engine.c](file:///home/enne2/dev/gameboy-hello/iso_test/engine.c) / [engine.h](file:///home/enne2/dev/gameboy-hello/iso_test/engine.h): Core del motore isometrico. Contiene la logica del labirinto, l'autotiling, lo scorrimento della telecamera, l'interpolazione del movimento e il supporto DAS.
*   [player.c](file:///home/enne2/dev/gameboy-hello/iso_test/player.c) / [player.h](file:///home/enne2/dev/gameboy-hello/iso_test/player.h) & [tiles.c](file:///home/enne2/dev/gameboy-hello/iso_test/tiles.c) / [tiles.h](file:///home/enne2/dev/gameboy-hello/iso_test/tiles.h): Asset grafici compilati (metasprite per il giocatore in 4 direzioni e varianti di piastrelle).
*   [generate_assets.py](file:///home/enne2/dev/gameboy-hello/iso_test/generate_assets.py): Script Python PIL per generare le texture di tiles e sprite a partire da matrici di pixel.

### Formato delle Coordinate Isometriche
Le coordinate logiche del labirinto $2D$ `(lx, ly)` vengono convertite in coordinate dello schermo Game Boy `(iso_x, iso_y)` per i background tiles tramite la seguente formula:
$$iso\_x = (lx - ly) \times 2 + 12$$
$$iso\_y = (lx + ly) \times 1 + 2$$
Questo permette di mappare una griglia ruotata a diamante perfettamente centrata nello spazio di visualizzazione.

---

## 🚀 Requisiti e Build

### Prerequisiti
1.  **GBDK-2020**: Installato in `/home/enne2/.local/gbdk`.
2.  **Python 3**: Con i seguenti pacchetti installati per i test e la rigenerazione degli asset:
    ```bash
    pip install --user Pillow pyboy opencv-python numpy
    ```

### Compilazione
Per compilare la ROM ed esportare `hello_iso.gb`:
```bash
make clean && make
```
Questo comando:
1.  Esegue `generate_assets.py` per creare `tiles.png` e `player.png`.
2.  Usa `png2asset` per convertire le PNG in codice sorgente C.
3.  Usa il compilatore `lcc` di GBDK per compilare e linkare tutti i file sorgente C nella ROM finale.

---

## 🧪 Test e Analisi Automatica

Il progetto include tre livelli di verifica headless per testare la correttezza logica e visuale senza avviare manualmente un emulatore grafico.

1.  **Generazione Screenshot**:
    ```bash
    python3 test_pyboy.py
    ```
    Avvia la ROM in PyBoy per 120 frame e salva un'immagine `hello_iso_gb.png` del display.

2.  **Test di Movimento in WRAM**:
    ```bash
    python3 test_movement.py
    ```
    Carica la ROM in PyBoy, legge lo stato della griglia del labirinto in WRAM (a partire dall'indirizzo `0xC0B1`) e simula la pressione dei tasti direzionali, verificando che la posizione del player (indirizzi `0xC4F4` e `0xC4F5`) cambi correttamente secondo le collisioni calcolate.

3.  **Rilevamento Glitch con OpenCV**:
    ```bash
    python3 opencv_analyze_tiles.py
    ```
    Utilizza OpenCV per esaminare lo screenshot generato, cercando disallineamenti o buchi neri tra le giunzioni delle piastrelle isometriche, segnalando eventuali problemi di rendering.
