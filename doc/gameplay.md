# Fisica e Controlli del Giocatore

Il movimento nel gioco è rigidamente vincolato alla griglia (Grid-Based), come nei vecchi RPG (Zelda, Pokémon), per semplificare le collisioni e la leggibilità degli ostacoli.

## State Machine (Blocco Input)

In `player_logic.c`, l'interpolazione fluida del movimento (il passaggio da una casella all'altra) richiede 16 frame. 
Durante questo lasso di tempo, la variabile `is_moving` è `true`. Qualsiasi input direzionale proveniente dai tasti (D-Pad) o dal tasto A viene totalmente ignorato finché il movimento sub-tile non si azzera (`move_progress == 16`). Questo impedisce movimenti diagonali non voluti o "scivolamenti" fuori griglia.

## Delayed Auto-Shift (DAS)

Leggere banalmente il D-Pad a 60 FPS renderebbe il personaggio incontrollabile (si muoverebbe di 4 caselle con una pressione leggermente prolungata). Leggere solo la "singola pressione" (keys_pressed) obbligherebbe a martellare il tasto per avanzare.

Abbiamo implementato un DAS, una tecnica tipica del Tetris:
- Al primo tocco, il giocatore si muove.
- Se si continua a tenere premuto, l'input viene ignorato per `DAS_DELAY` frames.
- Superato il delay, l'input si ripete in automatico ogni `DAS_REPEAT` frames.
Questo rende la navigazione dei corridoi estremamente fluida e confortevole.

## Il Salto e il Costo in Stamina

Tenendo premuto il tasto `A` assieme a una direzione direzionale, il giocatore scavalca il blocco adiacente atterrando due tile più in là.
Condizioni per il salto:
1. La casella di destinazione (`X+2`, `Y+2`) deve essere libera.
2. La casella intermedia saltata (`X+1`, `Y+1`) DEVE essere un muro (non si può saltare a vuoto sui corridoi).
3. Il giocatore deve avere almeno 60 punti Stamina.

La stamina si ricarica di 1 punto ogni secondo. Eseguire un salto costa 60 punti, disabilitando ulteriori balzi per un minuto intero. Questo lo rende una manovra evasiva salva-vita estrema e non uno strumento da spam abusivo.
Visivamente, l'altezza del salto non altera la logica (sempre 2D Grid), ma solo il rendering in `update_player_sprite()`, in cui sottraiamo al posizionamento verticale la formula parabolica `x * (16 - x) / 4`.

## La Corsa e il Costo in Stamina

Tenendo premuto il tasto `B` assieme a una direzione direzionale, il giocatore si mette a correre:
la transizione tra tile dura **8 frame** invece di 16 (l'incremento di `move_progress` raddoppia, mentre la formula LERP a punto fisso `>> 4` resta invariata e raggiunge il target in metà tempo). Ogni tile corso consuma **10 punti Stamina**.
Il DAS diventa più rapido (`DAS_REPEAT_RUN = 2`) così da incatenare i tile fluidamente quando si tiene premuto B+direzione.
Se la Stamina scende sotto 10, B+direzione **ripiega silenziosamente su camminata normale** (16 frame, 0 costo); la corsa si riattiva da sola appena la stamina torna ≥ 10. La ricarica resta di 1 punto al secondo, quindi la corsa è uno strumento a scatto: da pieno (100) si possono percorrere fino a 10 tile, dopodiché serve tempo per ricaricarla.

## Progressione dei Livelli

Il gioco parte dal **livello 1**. Raggiungere la botola (casella traguardo) significa "sprofondare più giù" (*Going Deeper*): alla pressione di START il livello viene **incrementato** e viene generato un nuovo labirinto. La sconfitta (cattura da parte del fantasma) riporta invece al **livello 1**.

L'indicatore `L<n>` è mostrato in **alto a sinistra** tramite tre sprite hardware (OAM ID 23–25), disegnati dall'asset `level.png` (11 glifi 8x16: 'L', '0'–'9'). Le decine vengono mostrate solo dal livello 10 in poi (sotto, lo sprite decine è spostato fuori schermo). Come la barra stamina (in alto a destra), l'indicatore è a coordinate-schermo fisse e indipendente dallo scroll isometrico, e viene nascosto durante il game over e sul titolo. La base VRAM dei glifi è allineata a un indice **pari** perché in modalità sprite 8x16 l'hardware ignora il bit meno significativo dell'indice tile.
