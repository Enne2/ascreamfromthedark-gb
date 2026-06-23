# Intelligenza Artificiale (Il Fantasma)

Il gioco utilizza un inseguitore, soprannominato "Il Fantasma", che bracca il giocatore all'interno del labirinto. Poiché il giocatore si muove velocemente, l'AI del fantasma richiede limiti artificiali per risultare un nemico superabile e bilanciato.

## Pathfinding: Perché "Greedy" e non A*?

Sui sistemi moderni o su griglie piccole, l'A-Star (A*) è l'algoritmo standard per il pathfinding dei nemici. Calcola il percorso perfetto evitando vicoli ciechi. 
Sul Game Boy (CPU 4 MHz), gestire la memoria (heap, nodi) richiesta da A* per un array 7x7 genererebbe ritardi nei frame (frame drops) inammissibili per un gioco real-time.

La soluzione implementata è un approccio **Greedy (Goloso)**:
Ad ogni passo, il fantasma verifica le 4 celle a lui adiacenti (Nord, Sud, Est, Ovest). Tra quelle calpestabili (non muri), sceglie quella la cui coordinata rende **minima la distanza spaziale al quadrato verso il giocatore** (`dx^2 + dy^2`).
Non usiamo la radice quadrata (necessaria per calcolare la distanza esatta euclidea) perché troppo costosa per la CPU; dal momento che stiamo solo comparando quale distanza sia minore, i quadrati bastano e avanzano matematicamente (`A < B <=> A^2 < B^2`).

Un algoritmo Greedy tende a incastrarsi in ostacoli a forma di U, ma essendo questo un labirinto dinamico pieno di loop a corridoio singolo, questo "difetto" si trasforma in una dinamica di gioco: i giocatori astuti possono sfruttare il level design per confondere l'AI e aggirarla.

## Attivazione e Cooldown

Il fantasma non parte immediatamente alla carica. Usa la distanza di Chebyshev per "vedere":
```c
if (dist <= 2) { // Inizia a muoversi }
```
Ovvero, inizia l'inseguimento solo quando entra nel riquadro visivo del giocatore (5x5, distanza <= 2).

Inoltre, il fantasma impiega 16 frame per muoversi da un blocco all'altro (come il player), ma è limitato dalla variabile `enemy_cooldown = 60`. Dopo ogni singolo passo, rimane congelato per 1 secondo intero prima di poterne fare un altro. Questo garantisce che il fantasma sia più lento del giocatore e ti costringe, qualora commettessi un errore, a usare rapidamente la meccanica di Salto Evasivo e seminarlo.

## Hitbox Pixel-Perfect

Nonostante la mappa sia calcolata su una pura griglia logica bidimensionale (1 passo = 1 casella X,Y), la condizione di "Sconfitta" non si basa sul fatto che il giocatore e il fantasma occupino la medesima casella logica contemporaneamente. Si controlla invece che le coordinate fisiche (i veri e propri **pixel** renderizzati sullo schermo del Game Boy) si sovrappongano con un margine di errore basso (12 pixel in orizzontale e 6 in verticale). 
Questo rende la morte "giusta" agli occhi dell'utente e permette scambi per il rotto della cuffia!
