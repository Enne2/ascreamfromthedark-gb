# Sintesi Audio e Musica

Tutto l'audio del gioco è prodotto internamente manipolando a basso livello i 4 canali audio (APU) registrati direttamente in memoria hardware del Game Boy (da `NR10_REG` a `NR52_REG`).

L'architettura separa completamente la logica audio da `engine.c` nel file isolato `sound.c`.

## Hardware Audio Channels (APU)
Il Game Boy dispone di 4 canali dedicati:
1. **Canale 1 (Pulse 1)**: Onda quadra con sweep (glissando automatico del pitch).
2. **Canale 2 (Pulse 2)**: Onda quadra senza sweep. Ideale per la base musicale.
3. **Canale 3 (Wave)**: Onda personalizzabile definita in RAM (qui non utilizzata).
4. **Canale 4 (Noise)**: Generatore di rumore pseudo-casuale bianco, usato per batterie ed effetti.

## Il Sequencer via Interrupt VBL
L'intera colonna sonora viene eseguita senza bloccare mai l'esecuzione del codice di rendering o della CPU.
La funzione `play_music_tick` viene agganciata al **Vertical Blanking (VBL) Interrupt** (`add_VBL()`), che scatta magicamente tra il disegno di un frame video e il successivo sul display a circa 60 Hz.
Ogni chiamata incrementa un timer logico; quando il timer supera la durata della nota impostata, il sequencer aggiorna l'indice dell'array passandolo ai registri e suonando fisicamente il suono.

## Illusioni Audio (Arpeggi e Polifonia Fittizia)
Il chip GBDK può suonare solo un singolo tono per canale alla volta. 
Per la "Fanfara di Vittoria" e i momenti di forte tensione, per imitare accordi (che richiederebbero 3 canali), usiamo gli **Arpeggi Veloci**.
Una melodia arpeggiata è un elenco di tre note (Es: Do-Mi-Sol) suonate in un loop talmente veloce che l'orecchio umano le fonde percependo un accordo polifonico. Nel codice, le note `N_C4`, `N_E4`, `N_G4` si susseguono ogni pochi frame (timer = 8 frame/tick).

## Il Rumore come Percussione
Durante la triste sequenza in tonalità minore del "Game Over", il Canale 4 del Rumore viene attivato sincopatamente:
```c
if (step % 8 == 0) {
    NR41_REG = 0x01;
    NR42_REG = 0xB2; // Decadimento rapidissimo per dare un colpo percussivo
    NR43_REG = (step < 64) ? 0x68 : 0x42; // Varia la frequenza: Thud basso vs Piatto (Crash) acuto
    NR44_REG = 0x80;
}
```
Questo simula il battito di un tamburo e i piatti, donando drammaticità alla scena.
