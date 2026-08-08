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

## Flush Incrementale (Dirty Rectangle con Wrap)

`draw_map` compone `map_buffer` (32×32) disegnando solo la finestra fog, poi trasferisce al background hardware **solo l'unione fra i bounds isometrici precedenti e correnti** (dirty rectangle):

- l'area nuova rende visibile il nuovo fog;
- l'area vecchia trasferisce gli zero necessari a cancellare il bordo uscente;
- il rettangolo viene diviso in al massimo quattro segmenti quando attraversa il bordo circolare 32×32 (`flush_wrapped_map_rect`);
- il primo frame dopo titolo/intermezzo/cambio livello invalida la cache e forza un full flush da 1.024 byte;
- un salto di coordinate che estende l'unione oltre una rivoluzione della tilemap usa lo stesso fallback.

Costo per un passo interno: fino a 242 byte con fog raggio 2 (22×11 tile) e 98 byte con raggio 1 (14×7), contro i 512 byte del vecchio flush fisso a 16 righe.

`draw_map` è chiamato **una sola volta per passo** (a metà movimento, `move_progress == 8`): il redraw a completamento è stato eliminato perché produceva byte identici (stesso centro, stessa mappa, stesso fog).

## HUD via Sprite

### Barra Stamina (alto destra)
5 sprite (OAM 18-22), coordinate schermo fisse (indipendenti dallo scroll). Conversione `stamina*40/100` → pixel. Tile caricati a `STAMINA_SPRITE_BASE` (152, base **pari** dedicata: in modalità 8x16 l'hardware ignora il bit basso dell'indice) per evitare overlap VRAM con i tile del background (workaround commit `93deb35`, corretto in release 2026-08-08).

### Indicatore Livello (alto sinistra)
3 sprite (OAM 23-25) che mostrano `L<n>` usando l'asset `level.png` (11 glifi 8×16: L, 0-9). Base VRAM `LEVEL_SPRITE_BASE` (178, pari, subito dopo i tile della stamina). Generato con `png2asset -keep_duplicate_tiles` per ordine tile prevedibile. Nascosto durante game over.

### Player Sprite
Metasprite 16×16 (OAM 0-1), 8 frame (4 direzioni × 2 frame camminata). Arco parabolico per il salto: `y_offset = (move_progress * (16 - move_progress)) >> 2`. Animazione camminata: `frame_offset = (move_progress >> 2) & 1` (più veloce in corsa, dato che move_progress incrementa di 2).

### Enemy Sprites
Fino a 8 metasprite 16×16 (OAM 2+i*2), palette invertita (OBP1 = 0x1B, fantasma bianco). Renderizzati solo se entro `fog_radius` e on-screen; altrimenti spostati offscreen (0,0).