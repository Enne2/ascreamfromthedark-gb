# Motore Grafico e Rendering

## Proiezione Isometrica

Il Game Boy ha hardware per griglie 2D piatte. Per ottenere l'isometrica 2.5D, trasformiamo le coordinate logiche `(lx, ly)` in coordinate schermo:

```c
// Coordinate tile (background map)
iso_x = (lx - ly) * 2 + 12;   // tile 32x16 -> metà larghezza
iso_y = (lx + ly) * 1 + 2;    // tile altezza 8px

// Coordinate pixel (per camera/collisione)
px = (lx - ly) * 16 + 96;
py = (lx + ly) * 8  + 16;
```

Camera centrata: `scroll_x = px - 64`, `scroll_y = py - 72`. Il player sprite è fisso al centro schermo (OAM 88,88); è il mondo a scorrere.

## Fog of War Scalabile

La visibilità usa la **distanza di Chebyshev** `max(|dx|, |dy|)` (no sqrt, no lookup table). Il raggio è la variabile globale `fog_radius`:

```c
if (dist > fog_radius) continue;          // nascondi
if (dist == fog_radius) -> tile scuro     // anello di penombra
if (dist <  fog_radius) -> tile normale   // zona illuminata
```

- **Livelli 1-6**: `fog_radius = 2` → finestra 5×5.
- **Livelli 7-8**: `fog_radius = 1` → finestra 3×3 (nebbia più stretta, più difficoltà).

Il nemico si attiva e viene renderizzato solo se entro `fog_radius`, coerente con la nebbia.

## Auto-Tiling e Multi-Pass Rendering

### Bitmasking
Ogni pavimento calcola una maschera sui vicini (TL, TR, BL, BR) per selezionare la variante grafica corretta (bordi arrotondati, angoli). 16 varianti × 2 stili alternati a scacchiera (`is_alt = (lx+ly)%2`). Le celle a `dist == fog_radius` usano varianti più scure ("Tile Dark") per simulare l'affievolimento della luce.

### Painter's Algorithm (2 passate)
Il background del Game Boy non ha trasparenze hardware. Per gestire l'overlapping isometrico:
1. **Pass 1**: pavimenti normali (bitmasking dinamico degli angoli).
2. **Pass 2**: la botola (oggetto complesso con maschera a 4 vicini, 243+81+162 varianti) disegnata per ultima, sovrascrive i pavimenti frontali ma si fonde grazie alle maschere dei propri angoli inferiori.

Questo preserva la grafica 3D della botola senza usare sprite hardware (evitando flickering per il limite di 10 sprite/scanline).

## Flush Dinamico a 16 Righe

`draw_map` azzera `map_buffer` (32×32), disegna solo la finestra fog, poi trasferisce al background hardware. Il flush è **dinamico a 16 righe** centrato sulla `iso_y` del centro di disegno, con gestione del wrap della mappa 32×32:

```c
int16_t center_iso_y = center_x + center_y + 2;
uint8_t start = (center_iso_y - 8) & 31;
if (start + 16 <= 32) {
    set_bkg_tiles(0, start, 32, 16, &map_buffer[start * 32]);
} else {
    // wrap: due chiamate
    set_bkg_tiles(0, start, 32, 32 - start, &map_buffer[start * 32]);
    set_bkg_tiles(0, 0, 32, 16 - (32 - start), map_buffer);
}
```

16 righe (512 byte) mantengono le prestazioni originali. Il flush è centrato dinamicamente perché con labirinti grandi (fino a 21×21) la finestra fog, in coordinate iso assolute, wrappa fuori dal vecchio range fisso 2-17.

`draw_map` è chiamato solo ai passi del movimento (progress 8 e completamento), non ogni frame.

## HUD via Sprite

### Barra Stamina (alto destra)
5 sprite (OAM 18-22), coordinate schermo fisse (indipendenti dallo scroll). Conversione `stamina*40/100` → pixel. Tile caricati a `tiles_TILE_COUNT` (indici ≥128) per evitare overlap VRAM con i tile del background (workaround commit `93deb35`).

### Indicatore Livello (alto sinistra)
3 sprite (OAM 23-25) che mostrano `L<n>` usando l'asset `level.png` (11 glifi 8×16: L, 0-9). Base VRAM allineata a indice **pari** (in modalità 8x16 l'hardware ignora il LSB del tile index). Generato con `png2asset -keep_duplicate_tiles` per ordine tile prevedibile. Nascosto durante game over.

### Player Sprite
Metasprite 16×16 (OAM 0-1), 8 frame (4 direzioni × 2 frame camminata). Arco parabolico per il salto: `y_offset = (move_progress * (16 - move_progress)) >> 2`. Animazione camminata: `frame_offset = (move_progress >> 2) & 1` (più veloce in corsa, dato che move_progress incrementa di 2).

### Enemy Sprites
Fino a 8 metasprite 16×16 (OAM 2+i*2), palette invertita (OBP1 = 0x1B, fantasma bianco). Renderizzati solo se entro `fog_radius` e on-screen; altrimenti spostati offscreen (0,0).