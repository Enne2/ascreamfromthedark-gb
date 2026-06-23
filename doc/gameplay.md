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
