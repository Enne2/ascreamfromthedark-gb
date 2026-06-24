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
Invece di cercare il punto matematicamente più lontano dalla partenza, l'algoritmo attuale sceglie un **punto casuale sul bordo sud** della mappa (`y = MAP_SIZE - 2`) tra le celle calpestabili di quella riga. Questo permette alla botola di apparire in una posizione imprevedibile lungo il bordo sud ad ogni partita.
Se, per un caso limite, la riga in fondo fosse inaccessibile, esiste un **fallback estremo** che posiziona la botola nell'angolo `(MAP_SIZE-2, MAP_SIZE-2)`.

Nota: storicamente il posizionamento usava la **Distanza di Manhattan** massima rispetto a `1,1`; il comportamento è stato cambiato per aumentare la varietà delle partite. La botola è disegnata con un oggetto complesso a maschera 4-vicini nel Pass 2 del renderer (vedi `graphics.md`).
