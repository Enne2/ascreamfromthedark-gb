# Motore Grafico e Rendering

## Proiezione Isometrica

Il Game Boy possiede un hardware progettato per griglie 2D piatte (scrolling orizzontale/verticale). Per ottenere un effetto isometrico 3D, trasformiamo matematicamente le coordinate logiche della griglia `(X, Y)` in pixel schermo `(iso_x, iso_y)`.

La formula utilizzata in `render.c` è:
```c
int8_t iso_x = (lx - ly) * 2 + 12; 
int8_t iso_y = (lx + ly) * 1 + 2; 
```
Questa trasformazione ruota la mappa di 45 gradi e la appiattisce sull'asse Y (rapporto 2:1, tipico dell'isometrico pixel-art).

## Ottimizzazione della Mappa

Aggiornare l'intera background map hardware del Game Boy (32x32 tiles, 1024 bytes) ad ogni "passo" del giocatore causerebbe gravissimi cali di framerate (lag) e sfarfallii visivi.
La soluzione implementata prevede di aggiornare *solo* le 16 righe visibili sullo schermo (160x144 pixel = 20x18 tiles) durante la funzione `draw_map`:
```c
set_bkg_tiles(0, 2, 32, 16, &map_buffer[2 * 32]);
```

## Fog of War e Distanza di Chebyshev

Per aumentare la tensione e oscurare il labirinto, il gioco disegna solo i pavimenti vicini al giocatore. Invece di calcolare un cerchio reale (distanza euclidea) che richiederebbe una CPU avida di risorse matematiche (radici quadrate o lookup tables), usiamo la **Distanza di Chebyshev**:
```c
int8_t dist = max(abs(dx), abs(dy));
if (dist > 2) continue; // Nascondi
```
Questo crea un quadrato di visibilità (5x5 celle) centrato sul giocatore, perfetto per le dinamiche a griglia.

## Auto-Tiling e Illuminazione

Il modulo di rendering controlla i vicini logici (Nord, Sud, Est, Ovest) di ogni casella per applicare la grafica giusta (es. muri arrotondati e non tagliati). Questo avviene tramite una maschera di bit (`mask`).
Inoltre, le celle a distanza Chebyshev pari a 2 (i bordi della visibilità) subiscono un cambio di offset grafico (`v = 32 + mask` o `v = 48 + mask`), prelevando dal tileset varianti più scure ("Tile Dark"). Questo simula l'affievolirsi della luce prima dell'oscurità totale.

## Gestione Overlapping Isometrico (Multi-Pass Rendering)

Nei giochi isometrici basati su tile, la proiezione genera sovrapposizioni (overlapping) tra i macro-blocchi. Dato che il background del Game Boy non supporta vere trasparenze hardware (un tile sovrascrive interamente quello sottostante), i tile disegnati per ultimi "tagliano" quelli precedenti con i loro angoli piatti.
Per preservare la complessa grafica 3D del traguardo (le scale) ed evitare l'esaurimento della ristrettissima VRAM (limite di 256 tile) tipico degli scenari pre-renderizzati combinatori, l'engine utilizza una strategia ibrida:
1. **Bitmasking:** I pavimenti piatti ricolorano dinamicamente i propri angoli trasparenti in base al colore dei vicini, creando l'illusione di un ritaglio perfetto.
2. **Painter's Algorithm (Pass Multiplo):** I pavimenti vengono renderizzati nel Pass 1, mentre gli oggetti complessi (come la casella di Vittoria) vengono disegnati rigorosamente in un Pass 2 successivo. Disegnandola per ultima, la scala sovrascrive i pavimenti frontali ma, grazie al Bitmasking dei propri angoli inferiori, si fonde con essi in modo invisibile. Ciò preserva interamente il disegno 3D senza richiedere sprite hardware addizionali (i quali causerebbero "flickering" per il rigido limite hardware di 10 sprite per scanline orizzontale).
