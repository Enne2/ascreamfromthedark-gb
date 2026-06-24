# Generazione Procedurale del Livello

## Algoritmo Depth-First Search (DFS)

Per garantire che ogni sessione di gioco sia unica, il labirinto viene generato proceduralmente ad ogni avvio (usando `DIV_REG` hardware del Game Boy come seed pseudo-casuale).

L'algoritmo utilizzato in `maze.c` è un **Depth-First Search (DFS)** con Backtracking, modellato per creare un "Perfect Maze" (labirinto perfetto in cui ogni cella è raggiungibile tramite un unico percorso possibile e senza cicli).
La mappa è concettualmente divisa in:
- Celle dispari (es. `1,1`, `1,3`): "Stanze"
- Celle pari: "Muri Divisori"

L'algoritmo parte da `1,1`, sceglie un vicino dispari casuale non visitato, abbatte il muro divisorio pari nel mezzo e avanza, salvando le posizioni in uno stack per poter tornare indietro (backtracking) quando finisce in un vicolo cieco.

## Rottura del Perfect Maze (Loop Generation)

Un "Perfect Maze" è frustrante in un gioco di inseguimento, perché intrappola il giocatore nei vicoli ciechi senza via di scampo.
Pertanto, è stata aggiunta una *Fase 2* alla generazione: l'algoritmo scansiona i muri rimanenti e, se un muro divide due stanze adiacenti, lo abbatte con una probabilità del 15%.
Questo genera anelli (loop) all'interno del labirinto, permettendo al giocatore tattiche evasive per aggirare il fantasma.

## Posizionamento del Traguardo (La Botola)

La casella traguardo è una **botola** nel terreno (ID 2) che il giocatore deve raggiungere per "sprofondare più giù" (*Going Deeper*) e avanzare di livello.
La botola viene piazzata su una qualunque cella calpestabile a **sufficiente distanza** dalla casella di partenza del giocatore `(1,1)`. Si raccolgono tutte le celle `maze[y][x] == 1` la cui distanza di Chebyshev da `(1,1)` sia `>= MIN_GOAL_DIST` (3) e se ne sceglie una a caso. In questo modo il traguardo è sempre lontano dall'inizio ma può trovarsi su una qualunque tile del labirinto, non più vincolato al bordo sud.
Se, per un caso limite, nessuna cella fosse a sufficienza distante (teoricamente impossibile in un perfect maze 7x7 con partenza 1,1), esiste un **fallback estremo** che posiziona la botola nella cella calpestabile più lontana in assoluto da `(1,1)`.

La distanza di Chebyshev è coerente col resto dell'engine (fog of war, attivazione del nemico). La botola è disegnata con un oggetto complesso a maschera 4-vicini nel Pass 2 del renderer (vedi `graphics.md`).
