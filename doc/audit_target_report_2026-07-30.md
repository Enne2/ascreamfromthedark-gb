# A Scream from the Dark — audit di codice, documentazione e target

Data dell'audit: **30 luglio 2026**  
Snapshot analizzato: `main` / `a8a6a32` (`Aggiungi suono di caduta nel vuoto`)  
Target dichiarato: Game Boy DMG, eseguibile anche su CGB in modalità compatibilità  
Toolchain locale: GBDK-2020 con SDCC 4.5.1

## 1. Sintesi esecutiva

Il progetto è un survival-horror isometrico tecnicamente interessante e già
eseguibile. La ROM corrente compila, si avvia in PyBoy, mostra correttamente
titolo, introduzione, istruzioni e gameplay, e rispetta il formato di una
cartuccia Game Boy ROM-only da 32 KiB.

L'architettura runtime è migliore di quanto suggerisca la storia del progetto:
il monolite è stato diviso in moduli riconoscibili, i calcoli critici sono
interi, le strutture dati sono dimensionate in modo compatibile con la WRAM e
la progressione 7×7 → 21×21 è realmente implementata.

Lo stato corrente non è però ancora “release-ready”. I problemi più importanti
sono:

1. **La build documentata non è riproducibile:** `make clean && make` elimina
   sette sorgenti in `src/screens/` e poi fallisce perché nessuna regola li
   ricrea.
2. **La barra stamina ha un errore di caricamento VRAM in modalità sprite
   8×16:** usa una base dispari e chiede di copiare 52 tile da un array che ne
   contiene 26. Il risultato è una lettura oltre la fine dell'asset e tile
   stamina sfalsati.
3. **Documentazione e codice sono divergenti:** salto rischioso, schermata di
   morte, musica del titolo, durata dei brani, schermate disponibili e pipeline
   asset sono descritti in modo non più corretto.
4. **La suite di test è in larga parte manuale o non eseguibile dai percorsi
   dichiarati:** diversi script cercano ROM e file `.noi` nella directory
   sbagliata; nessun test automatico protegge la build pulita, la VRAM o la
   progressione.
5. **Il budget per scanline OAM non è garantito:** il totale OAM è entro il
   limite, ma cinque o più fantasmi allineati verticalmente al giocatore possono
   superare i 10 oggetti hardware sulla stessa scanline.

Valutazione sintetica:

| Area | Valutazione | Nota |
|---|---:|---|
| Idea e uso del target | 8/10 | Fog, isometria e inseguimento sfruttano bene i vincoli |
| Architettura runtime | 7/10 | Modulare e leggibile, ma molto stato globale |
| Correttezza sul target | 5/10 | Buona base; bug VRAM e budget scanline da risolvere |
| Build e riproducibilità | 3/10 | La clean build fallisce e rigenera file versionati |
| Test | 3/10 | Smoke test possibile, automazione fragile/stale |
| Documentazione | 4/10 | Ampia ma non sincronizzata con HEAD |
| Prontezza per release fisica | 4/10 | ROM valida, ma servono fix e test su hardware |

## 2. Perimetro e metodo

Sono stati esaminati:

- tutti i file versionati elencati da Git;
- i sorgenti C/H runtime, i test C e gli asset C generati;
- i 21 script Python versionati e gli script non tracciati presenti nel working
  tree;
- README e tutti i documenti sotto `doc/`;
- Makefile, output del linker, header della ROM e simboli `.noi`;
- cronologia Git recente, per distinguere comportamento attuale e descrizioni
  storiche;
- avvio headless della ROM tramite PyBoy.

Il repository contiene 43 file C/H versionati (6.834 righe, incluse 3.138 righe
di asset C generati), 21 script Python versionati (2.074 righe) e 666 righe di
documentazione Markdown prima di questo audit.

Le numerose immagini, gli script di riscrittura e gli asset `final_victory` /
`level_ui` non tracciati sono stati considerati come **lavoro locale in corso**:
non fanno parte della ROM prodotta dal Makefile corrente e non sono stati
modificati.

## 3. Caratteristiche reali del target

### 3.1 Hardware rilevante

Il DMG dispone di:

- schermo 160×144, grafica a tile 8×8 e indici colore 2 bpp;
- 8 KiB di VRAM;
- 8 KiB di WRAM indirizzabile tra `$C000` e `$DFFF`;
- 40 oggetti hardware in OAM, ma non più di 10 selezionabili per scanline;
- sprite 8×8 oppure 8×16;
- quattro canali audio: due pulse, uno wave e uno noise;
- spazio ROM lineare di 32 KiB senza MBC; ROM più grandi richiedono banking.

Fonti tecniche: [Pan Docs: mappa di memoria](https://gbdev.io/pandocs/Memory_Map.html),
[grafica](https://gbdev.io/pandocs/Graphics.html),
[OAM](https://gbdev.io/pandocs/OAM.html),
[registri audio](https://gbdev.io/pandocs/Audio_Registers.html) e
[GBDK: ROM banking e MBC](https://gbdk.org/docs/api/docs_rombanking_mbcs.html).

Due vincoli sono particolarmente importanti per questo codice:

- in modalità 8×16 l'hardware ignora il bit meno significativo dell'indice
  tile dello sprite; l'indice superiore deve quindi essere pari;
- VRAM e OAM non sono sempre accessibili alla CPU mentre il PPU disegna. Le API
  GBDK gestiscono normalmente l'attesa, ma copie grandi durante LCD attivo
  consumano tempo e possono produrre transizioni lunghe.

Fonti: [Pan Docs: OAM 8×16](https://gbdev.io/pandocs/OAM.html),
[accesso VRAM/OAM](https://gbdev.io/pandocs/Accessing_VRAM_and_OAM.html) e
[GBDK: accesso sicuro al display](https://gbdk.org/docs/api/docs_supported_consoles.html#autotoc_md159).

### 3.2 Profilo della ROM prodotta

La compilazione diretta dello snapshot corrente produce:

| Campo | Valore rilevato |
|---|---|
| Dimensione file | 32.768 byte |
| Tipo cartuccia | `0x00`: ROM only |
| Codice dimensione ROM | `0x00`: 2 bank / 32 KiB |
| RAM cartuccia | nessuna |
| Flag CGB | `0x00`: non CGB-enhanced |
| Flag SGB | disabilitato |
| Titolo header | vuoto |
| Destinazione | `0x00`, Giappone (default toolchain) |
| Checksum header | valido (`0x53`) |
| Checksum globale | valido (`0xB929`) |

La dicitura corretta è quindi **gioco DMG compatibile con CGB**, non gioco che
usa caratteristiche CGB. Non sono presenti palette colore CGB, doppia velocità,
VRAM bank 1 o WRAM banked.

Prima di `$8000` restano circa **3.167 byte** liberi secondo la mappa del linker.
La ROM non è quindi “piena” in senso letterale, anche se il margine è abbastanza
ridotto da giustificare attenzione.

L'header dovrebbe essere completato con titolo, destinazione e, se desiderato,
flag CGB-compatible. GBDK espone queste opzioni tramite `-Wm-yn`, `-Wm-yj` e
`-Wm-yc`: [GBDK FAQ, ROM Header Settings](https://gbdk.org/docs/api/docs_faq.html#autotoc_md78).

### 3.3 Uso della memoria

La mappa del linker della build di audit riporta:

| Area | Uso |
|---|---:|
| `_CODE` | 26.826 byte |
| `_HOME` | 2.162 byte |
| initializer ROM | 88 byte |
| WRAM statica, inclusa shadow OAM | 2.956 byte |
| WRAM residua prima di `$E000` | circa 5.236 byte |
| HRAM | 19 byte |

La stima della documentazione di circa 3 KiB WRAM occupati è dunque plausibile.
Le voci principali sono `map_buffer[1024]`, `maze[441]` e i buffer statici di
generazione (`2×100 + 2×441` byte), oltre a stato globale e shadow OAM.

Il commento in `maze.c` che parla di 64 stanze massime è obsoleto: un 21×21
contiene 10×10 = **100** celle DFS dispari. La macro calcola correttamente 100,
quindi il difetto è documentale, non un overflow.

## 4. Architettura effettiva

### 4.1 Flusso principale

Il loop in `main.c` attende un VBlank, legge il joypad e instrada l'esecuzione:

```text
Titolo
 ├─ SELECT → crediti → B → titolo
 └─ START  → introduzione → un tasto → engine_init
                                      ↓
                              istruzioni iniziali
                                      ↓ B
                                  gameplay
                  ┌───────────────────┼──────────────────┐
               morte           botola L1–L7          botola L8
               retry           Going Deeper          finale
            stesso livello      livello + 1          ritorno titolo
```

`engine.c` orchestra inizializzazione e stati terminali; `player_logic.c` ed
`enemy_logic.c` aggiornano entità; `render.c` gestisce proiezione, fog e HUD;
`sound.c` è richiamato dall'ISR VBlank.

La separazione è sensata. Il costo è un forte accoppiamento tramite
`globals.h`: 50+ variabili globali o elementi di array rendono difficile testare
un modulo in isolamento e consentono transizioni di stato implicite.

### 4.2 Generazione procedurale

L'implementazione conferma:

- DFS iterativo su celle dispari;
- backtracking in array statici WRAM;
- apertura casuale del 15% dei muri con corridoi opposti;
- botola scelta fra celle a distanza Chebyshev almeno `map_size/2`;
- fallback alla cella calpestabile più lontana;
- dimensioni 7, 9, 11, 13, 15, 17, 19, 21.

Gli array sono correttamente limitati. `valid_x/y[441]` è sovradimensionato ma
sicuro. Lo spawn nemici tenta di rispettare distanza dal giocatore e dagli altri
fantasmi; tuttavia il fallback finale non ricontrolla la distanza fra nemici e
può sovrapporli in caso di molti fallimenti casuali.

Il seed è soltanto `DIV_REG`, cioè 8 bit dipendenti dal momento dell'input.
È adeguato a variare una partita arcade, non a offrire seed riproducibili o alta
entropia. Il registro DIV incrementa a 16.384 Hz su DMG:
[Pan Docs: timer e divider](https://gbdev.io/pandocs/Timer_and_Divider_Registers.html).

### 4.3 Movimento e gameplay

La proiezione e la LERP a punto fisso sono appropriate al target. Il movimento
usa passi logici su griglia e interpola per 16 unità; la corsa incrementa il
progresso di 2 e completa il passo in 8 frame.

Il comportamento reale del salto è diverso dai documenti:

- con 60+ stamina il salto oltre un muro è sicuro e costa 60;
- sotto 60 stamina il salto è comunque consentito;
- la probabilità di caduta è proporzionale alla stamina mancante;
- in caso di caduta il target diventa la cella muro intermedia e parte un game
  over dedicato.

A stamina zero, `roll < 255` produce 255 esiti di caduta su 256, non il 100%
indicato nel commento. Inoltre `DIV_REG` rende l'esito dipendente dal timing;
per un comportamento controllabile sarebbe preferibile usare lo stesso PRNG del
labirinto.

Il DAS funziona, ma il timer è aggiornato solo nei frame in cui il player non è
in movimento. La pausa di ripetizione avviene quindi **dopo** l'interpolazione,
non in parallelo a essa. È una scelta percepibile nei controlli e merita un test
di latenza invece di essere descritta soltanto come comportamento “Tetris”.

### 4.4 AI

L'AI greedy è coerente con il budget CPU: valuta fino a quattro vicini e usa
distanza quadratica senza radice. L'attivazione entro il fog limita ulteriormente
il costo.

Aspetti positivi:

- stato per entità in array fissi;
- massimo otto nemici;
- cooldown sfalsati;
- interpolazione e collisione in pixel;
- uscita immediata alla prima collisione fatale.

Limiti:

- non evita la cella occupata da un altro fantasma;
- può oscillare o bloccarsi in geometrie a U;
- il giocatore logico viene aggiornato dopo la fine del passo, mentre la
  collisione usa coordinate interpolate;
- `update_enemy_logic()` precede `update_player_movement()`, introducendo un
  frame di differenza fra il progresso player considerato dall'AI e quello poi
  renderizzato.

I primi due limiti possono essere accettabili come design; gli ultimi due
andrebbero coperti da test di collisione ai bordi.

### 4.5 Rendering

La parte più originale è il rendering isometrico:

- trasformazione logica → pixel/tile interamente intera;
- `map_buffer` 32×32 coerente con la tilemap hardware;
- fog Chebyshev 5×5 e poi 3×3;
- due passate per pavimento e botola;
- flush di 16 righe con wrap.

GBDK usa per default tile BG/Window a partire da `$8800`, mentre gli sprite
usano `$8000`; il codice sfrutta quindi correttamente i due modi di
indirizzamento della stessa VRAM:
[GBDK: impostazioni grafiche iniziali](https://gbdk.org/docs/api/docs_using_gbdk.html#autotoc_md191)
e [Pan Docs: LCDC.4](https://gbdev.io/pandocs/LCDC.html#lcdc4--bg-and-window-tile-data-area).

Il flush copia 512 byte a metà passo e a fine passo. È molto meno costoso di
1.024 byte ogni frame, ma rimane una copia importante mentre LCD è acceso. Le
schermate testuali copiano invece l'intera tilemap 32×32; nello smoke test
headless sono serviti molti frame prima che la funzione terminasse e tornasse a
leggere input. Per schermate statiche è preferibile spegnere il display durante
il caricamento o copiare solo 20×18 tile.

### 4.6 Audio

La strategia VBlank + registri APU è adatta a un sequencer semplice. I quattro
canali sono usati in modo coerente, con CH3 lasciato libero.

La documentazione musicale non corrisponde più al codice:

| Traccia | Codice corrente | Durata teorica a 59,7275 Hz |
|---|---:|---:|
| Titolo | 128 step × 8 frame | ~17,14 s, loop |
| Gameplay | 96 × 20 | ~32,15 s, loop |
| Game over | 128 × 10 | ~21,43 s |
| Finale | 192 × 14 | ~45,00 s, loop |
| Going Deeper | 96 × 15 | ~24,11 s |

README e documenti parlano ancora di 112 note e ~56 secondi per il titolo e di
~36 secondi per Going Deeper.

Alcune costanti di nota sono etichettate in modo scorretto: per esempio `N_D2`
ha lo stesso valore di `N_C2`, e `N_DS3` coincide con `N_CS3`. Se sono scelte
artistiche intenzionali, i nomi vanno corretti; altrimenti l'intonazione va
rigenerata dalla formula hardware.

## 5. Difetti e rischi, ordinati per priorità

### P0 — La clean build cancella sorgenti necessari

`Makefile:55` include nella stessa `rm -f`:

```make
src/title_bg.c src/screens/screens.c src/screens/instructions.c ...
```

`generate_c_assets` rigenera `title_bg.c`, ma nessun file sotto `src/screens/`.
In una copia temporanea del repository:

```text
$ make clean && make
...
make: *** No rule to make target 'src/screens/screens.c',
        needed by 'build/hello_iso.gb'.  Stop.
```

Impatto: la procedura principale documentata distrugge file versionati e rende
impossibile ricostruire la ROM senza ripristinarli da Git.

Correzione: il target `clean` deve eliminare solo output e asset C realmente
generati. I sorgenti handwritten `src/screens/*.c` non devono comparire.

### P0 — Caricamento stamina oltre array e base 8×16 dispari

Il codice esegue:

```c
set_sprite_data(tiles_TILE_COUNT, stamina_TILE_COUNT * 2, stamina_tiles);
```

Valori generati:

```text
tiles_TILE_COUNT   = 151
stamina_TILE_COUNT = 26
stamina_tiles      = 416 byte = 26 tile × 16 byte
```

Problemi:

1. vengono richiesti 52 tile (832 byte) da un array di 416 byte;
2. la base 151 è dispari;
3. gli indici mostrati sono `151 + tile_idx*2`, ma in modalità 8×16 l'hardware
   li arrotonda a `150 + tile_idx*2`.

La barra osservata nello smoke test appare infatti come una linea, non come i
segmenti generati. La formula corretta richiede una base pari dedicata e
`stamina_TILE_COUNT` come numero di tile da copiare. La documentazione hardware
che conferma l'azzeramento del bit basso è
[Pan Docs: OAM, Tile Index](https://gbdev.io/pandocs/OAM.html#byte-2--tile-index).

### P1 — Budget OAM per scanline non dimostrato

Nel gameplay massimo:

- player: 2 oggetti;
- otto fantasmi: fino a 16;
- stamina: 5;
- livello a una cifra: 2 visibili;
- totale allocato/attivo: 25, oppure 26 contando lo slot delle decine nascosto.

Il limite totale di 40 è rispettato. Il limite per scanline è però 10. Cinque
fantasmi 16×16 sulla stessa fascia verticale del player richiedono già
`5×2 + 2 = 12` oggetti, senza HUD. L'hardware seleziona i primi dieci in ordine
OAM, causando sparizione parziale degli ultimi.

La frase “sprite/scanline rispettato” nei documenti non è supportata da un test.
Servono un test sintetico worst-case e, se necessario, flicker controllato,
limite ai nemici visibili o rendering alternativo.

### P1 — Pipeline asset non riproducibile

`generate_images` non produce un file sentinella ed è una dipendenza sempre
eseguita di `generate_c_assets`; ogni build rigenera PNG e C versionati.

Con il `png2asset` locale, una rigenerazione pulita modifica molti asset C,
inclusi `next_level.c/h`, anche senza cambiamenti intenzionali. Una parte è
formattazione della versione del tool, ma il repository non dichiara o verifica
una versione esatta.

`next_level.c` viene generato ma non linkato. `victory.png` viene generato ma non
convertito/linkato. Questo mescola asset attivi, storici e sperimentali.

Correzione: scegliere un solo modello:

- asset C versionati e build che non li rigenera implicitamente; oppure
- PNG sorgente + versione GBDK fissata + regole file-to-file deterministiche,
  con verifica `git diff --exit-code`.

### P1 — Test non eseguibili come documentato

- `test_pyboy.py` cerca `hello_iso.gb` nella cwd, ma la ROM è in `build/`;
- `test_movement.py` cerca anche `hello_iso.noi`, che la main build non genera;
- legge `maze` come righe da 7 byte, mentre l'array reale ha stride 21;
- non supera titolo, intro e istruzioni prima di leggere il gameplay;
- `test_alignment.py` cerca `test_gameover.gb` nella cwd;
- `take_screenshot.py` usa la vecchia keyword PyBoy `window_type`;
- `opencv_analyze_tiles.py` scrive in un percorso assoluto esterno
  `.gemini/...`;
- i test C `test_going_deeper.c` e `test_stairs_connect.c` non hanno target
  Makefile e il secondo usa ancora il vecchio schema di maschere binarie.

I due test ROM principali compilano se invocati direttamente. Non costituiscono
però una suite automatica con asserzioni.

### P1 — Documentazione non sincronizzata

Inesattezze principali:

- salto sotto 60 stamina descritto come disabilitato;
- morte descritta con `claimed.png`, ma il codice usa testo IBM;
- `claimed.c/h` citati ma inesistenti;
- title theme descritto come 112 note / ~56 s anziché 128 / ~17 s;
- linee e dimensioni dei moduli storiche;
- sprite count indicato come ~27 anziché massimo gameplay 25 visibili;
- ROM descritta come piena, ma la mappa lascia ~3,1 KiB;
- schermate intro, crediti e istruzioni non integrate nell'indice tecnico;
- esito PyBoy dichiarato nel vecchio report non più riproducibile dagli script
  presenti.

### P2 — Header cartuccia incompleto

La ROM è tecnicamente valida, ma titolo vuoto, destinazione giapponese di
default e assenza di metadati riducono identificabilità su flashcart, dumper e
cataloghi.

### P2 — Portabilità della build

`GBDK_HOME = /home/enne2/.local/gbdk` rende la build specifica della macchina.
Usare `GBDK_HOME ?= ...`, ricerca in `PATH` o un container/toolchain dichiarato.

### P2 — Copie tilemap statiche troppo grandi

Intro, istruzioni, crediti e schermate terminali azzerano/copia­no 32×32 tile,
ma il display visibile è 20×18. Questo amplifica il tempo di transizione.

### P2 — Script di riscrittura pericolosi

Nel working tree non tracciato sono presenti numerosi `fix_*.py` e
`rewrite_*.py` che riscrivono sorgenti tramite regex. Non sono parte della build,
ma andrebbero spostati in un archivio o eliminati dopo averne estratto le
modifiche utili: applicarli allo snapshot attuale potrebbe regredire il codice.

## 6. Verifiche eseguite

### 6.1 Compilazione

Compilazione diretta della main ROM: **OK**.

Warning:

- due argomenti non usati in `title_update`;
- quattro warning SDCC 110 sul flusso modificato dall'ottimizzatore.

I warning 110 non dimostrano un bug, ma non dovrebbero essere liquidati come
easter egg senza testare la ROM ottimizzata.

Compilazione diretta ROM `test_gameover`: **OK**.  
Compilazione diretta ROM `test_finale`: **OK**.  
`make clean && make` in copia temporanea: **FAIL**, come descritto in P0.

### 6.2 Smoke test PyBoy

La ROM appena compilata è stata avviata in modalità DMG headless:

- titolo: renderizzato;
- START → intro: renderizzata;
- un tasto → istruzioni: renderizzate;
- B → gameplay: renderizzato;
- stato iniziale letto dai simboli: livello 1, mappa 7, fog 2, un nemico,
  stamina 100.

Lo smoke test conferma il percorso base, non la correttezza degli otto livelli,
delle collisioni o dell'audio su hardware reale.

### 6.3 Header e linker

- dimensione ROM: corretta;
- checksum header: corretto;
- checksum globale: corretto;
- nessun overflow ROM/WRAM segnalato dal linker;
- hash ROM di audit:
  `15e8a396aa40c45500068b1a4110f8d3a9c42851936a5c25371a04d85eff19ad`.

La ROM versionata in `build/hello_iso.gb` ha hash diverso dalla build corrente:
è quindi un artefatto precedente e non una prova di riproducibilità.

## 7. Piano di intervento consigliato

### Fase 1 — bloccare i difetti di rilascio

1. correggere `clean` e aggiungere un test CI `make clean && make`;
2. introdurre `STAMINA_SPRITE_BASE` pari e caricare esattamente 26 tile;
3. aggiungere nome/destinazione/versione all'header;
4. ricompilare e acquisire screenshot comparativi di HUD e livelli.

### Fase 2 — rendere la build deterministica

1. separare sorgenti handwritten e generati;
2. eliminare target/asset orfani dalla pipeline;
3. rendere `GBDK_HOME` configurabile;
4. fissare la versione GBDK/png2asset;
5. produrre `.map`, `.noi` e `.sym` anche per la ROM principale.

### Fase 3 — creare una vera suite headless

Un unico runner PyBoy dovrebbe:

1. superare titolo, intro e hint;
2. risolvere simboli dal `.noi`;
3. verificare livelli 1–8 e parametri di difficoltà;
4. usare stride `MAX_MAP_SIZE` per leggere `maze`;
5. forzare e verificare morte, Going Deeper e finale;
6. catturare HUD a stamina 0/50/100;
7. creare un worst-case con otto fantasmi sulla stessa fascia e rilevare
   dropout OAM;
8. fallire con exit code non zero in caso di regressione.

### Fase 4 — riallineare design e documentazione

1. decidere se il salto rischioso è la meccanica definitiva;
2. aggiornare README e capitoli tecnici dal codice verificato;
3. documentare intro, crediti, istruzioni e schermate testuali;
4. rigenerare tabella audio e frequenze da dati sorgente;
5. sostituire il vecchio report con un documento “as built” o marcarlo
   esplicitamente come storico.

### Fase 5 — validare il target fisico

Prima di una cartuccia:

- test su almeno DMG e CGB in compatibility mode;
- verifica audio con cuffie e speaker;
- test del seed/divider su accensioni ripetute;
- stress OAM ai livelli 7–8;
- misurazione delle pause dovute ai trasferimenti VRAM;
- test prolungato di tutti gli otto livelli e retry.

## 8. Giudizio finale

Il progetto non è un semplice demo: possiede un loop completo, progressione,
stati terminali, asset originali, musica e soluzioni specifiche per i limiti del
Game Boy. La scelta di un labirinto piccolo ma crescente, fog locale e AI greedy
è ben calibrata per ROM-only e CPU DMG.

La priorità non dovrebbe essere aggiungere altre feature. Il maggior valore ora
viene da consolidamento: clean build non distruttiva, correzione della stamina,
test automatici basati sui simboli e documentazione derivata dal comportamento
reale. Dopo questi interventi il progetto può passare da prototipo avanzato a
release candidata credibile per emulatori, flashcart e cartuccia fisica.
