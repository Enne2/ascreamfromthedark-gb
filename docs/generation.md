# Generazione Procedurale del Livello

## Algoritmo DFS con Backtracking

Il labirinto è generato proceduralmente ad ogni avvio (seed da `DIV_REG`). L'algoritmo è un **Depth-First Search (DFS) iterativo** con backtracking che crea un "perfect maze" (ogni cella raggiungibile, nessun ciclo):

1. La griglia `map_size × map_size` è divisa in **celle dispari = stanze** (1,1 / 1,3 / 3,1 ...) e **celle pari = muri divisori**.
2. Il DFS parte da `(1,1)`, sceglie un vicino dispari non visitato a distanza 2, abbatte il muro divisorio (media aritmetica delle coordinate), avanza.
3. Se nessun vicino disponibile, torna indietro (backtracking) usando uno stack.
4. Quando lo stack è vuoto, il labirinto è completo.

### Stack in WRAM (non sullo stack hardware)
Gli array di backtracking (`stack_x`, `stack_y`, `valid_x`, `valid_y`) sono **statici in WRAM** (non sullo stack hardware del LR35902), sized per `MAX_MAP_SIZE = 21`:
- `MAX_ROOMS = (21/2)² = 100` (massimo numero di stanze per 21×21)
- `MAX_CELLS = 21² = 441` (massimo numero di celle candidate)

Questo evita l'overflow dello stack hardware del Game Boy (che è piccolo).

## Dimensioni Crescenti col Livello

La dimensione del labirinto cresce di 2 tile per lato ad ogni livello:

| Livello | map_size | Stanze | Tile data |
|---------|----------|--------|-----------|
| 1 | 7×7 | 9 | 49 B |
| 2 | 9×9 | 16 | 81 B |
| 3 | 11×11 | 25 | 121 B |
| 4 | 13×13 | 36 | 169 B |
| 5 | 15×15 | 49 | 225 B |
| 6 | 17×17 | 64 | 289 B |
| 7 | 19×19 | 81 | 361 B |
| 8 | 21×21 | 100 | 441 B |

`map_size = MAP_SIZE + 2*(level-1)`, capped a `MAX_MAP_SIZE = 21`. Sempre dispari (per il pattern stanza/muro). L'array `maze` è allocato `[21][21]` (441 byte) e i moduli usano `map_size` come bound runtime.

## Rottura del Perfect Maze (Loop)

Un perfect maze frustra un gioco d'inseguimento (vicoli ciechi senza scampo). La **Fase 2** riapre casualmente il 15% dei muri che collegano due corridoi opposti, generando anelli (loop) che permettono al giocatore di aggirare il fantasma.

## Posizionamento della Botola

La botola (tile ID 2) è il traguardo. Viene piazzata su una cella calpestabile a **sufficiente distanza** dalla partenza `(1,1)`:

- Soglia: `min_goal = map_size / 2` (3 per 7×7, 10 per 21×21) — scala con la dimensione.
- Si raccolgono tutte le celle con `maze[y][x] == 1` e `chebyshev((1,1), (x,y)) >= min_goal`, se ne sceglie una a caso.
- Fallback: la cella calpestabile più lontana in assoluto da `(1,1)`.

La botola è disegnata con un oggetto complesso a maschera 4-vicini nel Pass 2 del renderer (vedi `graphics.md`).

## Spawn del Nemico

I fantasmi (`num_enemies = level`, capped 8) sono piazzati su celle calpestabili lontane ≥ `map_size/2` dal giocatore e ≥ 2 celle dagli altri fantasmi già piazzati. I cooldown iniziali sono sfasati (`enemy_step_cooldown + i*8`) per non sincronizzarli.