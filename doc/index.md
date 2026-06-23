# Game Boy Iso-Engine: Documentazione Tecnica

Benvenuto nella documentazione tecnica del progetto. Questo motore per Game Boy a 8-bit è stato progettato per dimostrare come tecniche avanzate (prospettiva isometrica, fog of war, generazione procedurale e intelligenza artificiale) possano essere implementate sulle ristrette risorse hardware del Game Boy (CPU Sharp LR35902 a 4.19 MHz, 8KB WRAM).

## Indice dei Capitoli

La documentazione è suddivisa in file separati, ognuno dedicato a un aspetto specifico dell'engine.

1. **[Architettura di Base](architecture.md)**
   Struttura del codice, organizzazione in moduli (src, assets, scripts) e gestione dello stato globale per evitare dipendenze circolari in C.

2. **[Motore Grafico e Rendering](graphics.md)**
   La matematica dietro la proiezione isometrica, l'ottimizzazione dell'auto-tiling, il sistema "Fog of War" basato sulla distanza di Chebyshev e la gestione dei metasprite.

3. **[Generazione Procedurale del Livello](generation.md)**
   Come l'algoritmo Depth-First Search (DFS) crea un labirinto perfetto, come vengono generati i loop per il gameplay e come la distanza di Manhattan posiziona il traguardo.

4. **[Fisica e Controlli del Giocatore](gameplay.md)**
   Il sistema di input con Delayed Auto-Shift (DAS), la State Machine rigida per l'allineamento alla griglia, e la complessa meccanica del salto con traiettoria parabolica e costo in Stamina.

5. **[Intelligenza Artificiale (Il Fantasma)](ai.md)**
   Perché il nemico usa un algoritmo Greedy invece di A*, il sistema di cooldown dei movimenti per bilanciare il gameplay, e la hitbox "Pixel-Perfect" che scatena il Game Over.

6. **[Sintesi Audio e Musica](audio.md)**
   Come l'engine manipola direttamente i registri hardware APU (Audio Processing Unit) per creare arpeggi finti, percussioni bianche (noise channel) e melodie atmosferiche.
