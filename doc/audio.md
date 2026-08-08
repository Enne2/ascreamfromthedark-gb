# Sintesi Audio e Musica

## Hardware APU (4 canali)

Il Game Boy ha 4 canali audio, manipolati direttamente via registri hardware (`NR10_REG` .. `NR52_REG`):

| Canale | Tipo | Uso nel gioco |
|--------|------|---------------|
| CH1 | Pulse + sweep | Melodie (title, gameover, finale), salto, cattura |
| CH2 | Pulse | Bassi, melodie sostenute, gameplay eerie |
| CH3 | Wave | Non utilizzato |
| CH4 | Noise | Percussioni (toll, crash, thud), effetti |

## Sequencer via VBL Interrupt

`play_music_tick` è agganciato al **Vertical Blanking Interrupt** (`add_VBL()`), ~60 Hz. Non blocca mai il rendering. Ad ogni VBL incrementa un timer; quando supera il periodo della nota, suona la nota corrente dall'array e avanza l'indice.

### Note frequencies
Le costanti `N_*` sono precalcolate come `(2048 - 131072/freq)` e scritte in `NR13/NR23` (low byte) e `NR14/NR24` (high byte | 0x80 trigger). Range: N_C2 (44, ~131 Hz) a N_A5 (1899, ~880 Hz).

Nota: `N_D2` (263) e `N_DS3` (1103) sono etichette storiche — `N_DS3` condivide il valore con `N_CS3` (1103), quindi nella salita cromatica del title bass la nota suonata è C#3, non D#3. Il valore non è stato modificato per non alterare la musica validata (vedi commento in `sound.c`).

## Tracce

### Title Theme (128 note, 3 canali, ~17 sec, loop)
Brano d'inseguimento veloce e d'azione. 128 note su 3 canali, 8 frame/nota:
- **CH1 melodia**: arpeggi ascendenti D-F-A-D (frase 1), C-E-G-C (frase 2), Bb-D-F-Bb (frase 3), poi melodia di tensione, salita cromatica (D4→D5) e climax su D5 ripetuto. Envelope staccato/urgente (NR12=0x92).
- **CH2 basso**: linea indipendente (`title_bass[128]`) pulsante (D3, A2, Bb2, F2), salita cromatica e pedale di D nel climax. Envelope sharp (NR22=0x91).
- **CH4 noise**: percussioni veloci — kick sul downbeat (ogni 4 step, NR43=0x73) e hi-hat sugli upbeat (ogni 2 step, NR43=0x20).

Struttura: arpeggio ascendente → tensione → climax (colpo di caccia) → discesa drammatica → cadenza con arresto improvviso. Ispirazione: Castlevania (arpeggi gotici), Metroid II (desolazione), Link's Awakening (melancolia onirica).

### Gameplay Theme (96 note, CH2, ~32 sec, loop)
Battito ritmico ansioso ("eerie pulse") in La minore → Re minore → Mi7. 20 frame/nota. Pattern ripetuto che accelera la tensione dell'inseguimento.

### Game Over (128 note, CH1+CH2+CH4, ~21 sec)
Concerto tragico polifonico. 16 accordi con intensificazione (arpeggi più alti nella seconda metà). Noise percussion: thud basso (NR43=0x68) per la prima metà, crash acuto (NR43=0x42) per la seconda. 10 frame/nota.

### Finale (192 note, CH1+CH2+CH4, ~45 sec, loop)
Brano dedicato per il finale tragico (livello 8). Lamento discendente in Re minore:
- **CH1**: melodia sommessa (NR12=0xA2, fade lungo).
- **CH2**: basso profondo (NR22=0xD1, fade lentissimo).
- **CH4**: rintocco medio (0x68) di default, crash (0x42) al climax (step 80/88/112), tonfo profondo (0x70) nell'abisso (step ≥160).

Struttura: lamento Dm-C-Bb-A7 → intensificazione con arpeggi alti (lo "scream") → crollo con basso che scende fino al Do più grave (N_C2) → silenzio. 14 frame/nota (sommesso). Loop infinito.

### Going Deeper (96 note, CH1+CH2, ~24 sec)
Melodia misteriosa discendente (Am → Fmaj7 → Dm → E7 → C aug → abisso). 15 frame/nota. Usata per la schermata di transizione tra livelli.

## Sound Effects

- **Salto**: pitch sweep up sul CH1 (NR10=0x15, sweep up).
- **Cattura (game over)**: slide down profondo sul CH1 (NR10=0x1E, sweep down, envelope rapido).
- **Beat drammatico iniziale (gameover/finale)**: NR21-NR24 triggerato al momento del game over.