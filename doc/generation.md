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

## Posizionamento del Traguardo (Vittoria)

La casella traguardo (il "Portale") deve essere logicamente il punto più lontano dalla partenza (situata in alto a sinistra a `1,1`).
Per trovarla, l'algoritmo calcola la **Distanza di Manhattan** (`|X1 - X2| + |Y1 - Y2|`) di ogni cella percorribile rispetto a `1,1`. La cella con il valore più alto viene designata con ID 2, trasformandola graficamente nel portale di fine livello.
