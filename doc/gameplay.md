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

Il gioco parte dal **livello 1**. Raggiungere la botola (casella traguardo) significa "sprofondare più giù" (*Going Deeper*): alla pressione di START il livello viene **incrementato** e viene generato un nuovo labirinto. In caso di sconfitta (cattura da parte del fantasma) si **ricomincia dallo stesso livello raggiunto**: il contatore non si azzera, solo il passaggio per il titolo (nuova partita) riparte da 1.

## Dimensione crescente del labirinto e difficoltà progressiva

Ad ogni livello la **dimensione del labirinto cresce di 2 tile per lato**: 7x7 (livello 1) fino a **21x21** (livello 8). La dimensione corrente è la variabile globale `map_size` (l'array `maze` è allocato con bound `MAX_MAP_SIZE` = 21). Il DFS genera un perfect maze su `map_size`x`map_size` (le celle dispari sono le stanze, per questo `map_size` è sempre dispari), poi lo rompe con i loop al 15% e posiziona la botola a distanza di Chebyshev ≥ `map_size/2` dalla partenza.

Oltre alla dimensione, ci sono altri **assi di difficoltà** che scalano col livello:
- **Numero di fantasmi**: `num_enemies = level` (capped a `MAX_ENEMIES` = 8). Ogni fantasma ha stato indipendente (array) e AI greedy propria; cooldown iniziali sfasati per non sincronizzarli.
- **Fantasma più veloce**: `enemy_step_cooldown = 60 - 7*(level-1)` (floor 10) — pausa più breve tra i passi ai livelli alti.
- **Stamina più lenta**: `stamina_recharge_rate = 60 + 12*(level-1)` — la barra si ricarica più lentamente.
- **Nebbia più stretta**: `fog_radius = 1` (3x3) dal livello 7 (invece di 2 / 5x5).

**Il gioco finisce dopo il livello 8**: superare la botola al livello 8 setta `game_over = 3` (finale) invece di 2 (Going Deeper). La schermata finale usa il font IBM ricaricato per stampare "YOU ESCAPED / THE DARKNESS / LEVEL 8 CLEARED / PRESS START"; START torna al titolo (nuova partita dal livello 1).

Poiché con labirinti grandi la finestra fog-of-war, proiettata in coordinate isometriche assolute, può cadere fuori dal vecchio range di righe flussato (2-17) a causa del wrapping della mappa 32x32, `draw_map` ora usa un flush **dinamico a 16 righe** centrato sulla iso_y del centro di disegno (con gestione del wrap via due `set_bkg_tiles`). Questo mantiene le prestazioni del progetto originale (16 righe = 512 byte) coprendo la nebbia in qualunque posizione.

L'indicatore `L<n>` è mostrato in **alto a sinistra** tramite tre sprite hardware (OAM ID 23–25), disegnati dall'asset `level.png` (11 glifi 8x16: 'L', '0'–'9'). Le decine vengono mostrate solo dal livello 10 in poi (sotto, lo sprite decine è spostato fuori schermo). Come la barra stamina (in alto a destra), l'indicatore è a coordinate-schermo fisse e indipendente dallo scroll isometrico, e viene nascosto durante il game over e sul titolo. La base VRAM dei glifi è allineata a un indice **pari** perché in modalità sprite 8x16 l'hardware ignora il bit meno significativo dell'indice tile.
