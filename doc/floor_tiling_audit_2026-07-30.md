# Audit del sistema di tiling del pavimento

- Data: **30 luglio 2026**
- Snapshot: `a8a6a32`
- Ambito: generazione asset in `scripts/generate_assets.py`, lookup table in
  `src/tiles.c` e compositing in `src/render.c`

## 1. Giudizio sintetico

Il sistema di tiling è **buono dal punto di vista grafico e concettuale**, ma
molto meno efficiente nella rappresentazione dei dati.

La soluzione risolve correttamente tre problemi non banali su Game Boy:

1. pavimenti isometrici 32×16 costruiti con tile hardware 8×8;
2. sovrapposizione tra celle secondo un painter's algorithm;
3. raccordi differenti fra vuoto, pavimento illuminato e anello di penombra.

L'idea più riuscita è lo stato ternario dei vicini. Il codice non usa realmente
una bitmask, come affermano alcuni commenti, ma una codifica in base 3:

```text
0 = vicino assente, muro o fuori dal fog
1 = vicino visibile e illuminato
2 = vicino visibile nell'anello scuro
```

Questa scelta evita bordi cromaticamente incoerenti fra zona chiara e
penombra. È più raffinata di un autotile binario tradizionale.

Il difetto principale è che vengono materializzate tutte le combinazioni come
macro-tile completi, nonostante ogni stato modifichi soltanto una coppia
indipendente di tile 8×8. La tabella da 2.884 byte può essere sostituita da
**160 byte senza cambiare un singolo pixel**.

Valutazione:

| Aspetto | Voto | Osservazione |
|---|---:|---|
| Qualità dell'idea | 8/10 | Buona traduzione dell'isometria sui vincoli DMG |
| Continuità visiva | 8/10 | Stati ternari e alternanza evitano stacchi netti |
| Uso VRAM | 6/10 | 151 tile sono gestibili ma occupano una quota importante |
| Uso ROM dei dati | 4/10 | La macro-map contiene circa 2,7 KiB evitabili |
| Costo runtime | 5/10 | Il disegno viene ripetuto due volte per la stessa cella |
| Manutenibilità | 5/10 | PNG alto 5.768 px e indici numerici impliciti |

## 2. Come funziona realmente

### 2.1 Macro-tile isometrico

Ogni cella logica è un diamante 32×16 pixel:

```text
32 × 16 pixel = 4 × 2 tile hardware = 8 indici nella BG map
```

La posizione è:

```c
iso_x = (lx - ly) * 2 + 12;
iso_y = (lx + ly) + 2;
```

Due celle adiacenti non sono semplicemente affiancate. Si sovrappongono:

- `lx + 1`: spostamento `(+2, +1)` tile hardware;
- `ly + 1`: spostamento `(-2, +1)`.

La metà superiore della cella disegnata dopo sostituisce quindi parte della
metà inferiore della precedente. È il meccanismo che crea la continuità
isometrica senza trasparenza nel background.

Il Game Boy usa tile 8×8 a 2 bpp e una tilemap di 32×32 elementi; riusare tile
è il modo naturale per risparmiare VRAM:
[Pan Docs, Graphics](https://gbdev.io/pandocs/Graphics.html).

### 2.2 Ordine di disegno

Il renderer attraversa `ly` e poi `lx`. Con la trasformazione scelta:

- la cella a est viene disegnata dopo e copre il raccordo inferiore destro;
- la cella a sud viene disegnata in una riga successiva e copre il raccordo
  inferiore sinistro.

Per questo il pavimento ordinario ha varianti soltanto per gli angoli:

```text
TL = vicino (lx - 1, ly)
TR = vicino (lx, ly - 1)
BL = sempre 0
BR = sempre 0
```

Gli angoli inferiori non devono conoscere i vicini futuri: saranno coperti dai
top corner delle celle disegnate dopo. È una buona ottimizzazione già presente
nel design.

### 2.3 Codifica ternaria

Per il pavimento:

```c
mask = state_tl + state_tr * 3;       // 3² = 9 combinazioni
```

Per la botola:

```c
mask = state_tl
     + state_tr * 3
     + state_bl * 9
     + state_br * 27;                 // 3⁴ = 81 combinazioni
```

La botola viene disegnata in una seconda passata, sopra tutti i pavimenti.
Proprio perché ignora l'ordine naturale, deve conoscere anche i due raccordi
inferiori.

La variabile si chiama `mask`, ma non è una bitmask: è un **indice in base 3**.
Correggere terminologia e commenti renderebbe il codice più comprensibile.

### 2.4 Stili

Ogni combinazione esiste in quattro gruppi:

| Gruppo | Illuminazione | Variante scacchiera |
|---:|---|---|
| 0 | chiara | A |
| 1 | chiara | B |
| 2 | scura | A |
| 3 | scura | B |

`is_alt = ((lx + ly) % 2 == 0)` crea una trama a scacchiera. L'anello con
`dist == fog_radius` usa i gruppi scuri.

Il DMG non dispone di palette differenti per ogni tile del background.
Eliminare gli asset scuri e applicare una palette locale a runtime non è quindi
possibile. Le palette per tile sono una funzione CGB e cambierebbero il target:
[Pan Docs, LCDC e tile data](https://gbdev.io/pandocs/LCDC.html) e
[GBDK, supporto piattaforme](https://gbdk.org/docs/api/docs_supported_consoles.html).

## 3. Costo misurato

### 3.1 Varianti generate

Il PNG `assets/tiles.png` misura 32×5.768 pixel e contiene:

| Categoria | Calcolo | Macro-tile |
|---|---:|---:|
| Pavimento | 9 stati × 4 gruppi | 36 |
| Botola | 81 stati × 4 gruppi | 324 |
| Totale | | 360 |

Ogni macro-tile contiene otto indici. Il file generato espone:

```text
tiles_map:   2.884 byte = 4 iniziali + 360 × 8
tiles_tiles: 2.416 byte = 151 tile unici × 16
palette:        64 byte
totale dati: 5.364 byte
```

`png2asset` deduplica già molto bene la grafica:

| Categoria | Tile 8×8 unici |
|---|---:|
| Vuoto | 1 |
| Pavimenti | 62 |
| Botola | 88 |
| Totale | 151 |

La deduplicazione dei pixel è quindi efficace. Il problema non è
`tiles_tiles`, ma `tiles_map`: il 53,8% dei dati dell'asset è una tabella di
combinazioni.

GBDK conferma che `png2asset` elimina i duplicati e può esportare solo il
tileset tramite `-tiles_only`:
[GBDK, png2asset](https://gbdk.org/docs/api/docs_toolchain_settings.html#png2asset-settings).

### 3.2 Costo di un aggiornamento

Una chiamata a `draw_map()`:

1. azzera 1.024 byte di `map_buffer`;
2. visita al massimo 25 celle con fog radius 2, oppure 9 con radius 1;
3. chiama `get_tile_state()` due volte per pavimento;
4. riesamina la stessa finestra in una seconda passata per trovare la botola;
5. scrive otto indici per ogni cella visibile;
6. trasferisce sempre 512 byte alla BG map hardware.

Durante ogni passo del giocatore viene chiamata:

```text
move_progress == 8  → draw_map(target_lx, target_ly)
move_progress == 16 → player = target; draw_map(player_lx, player_ly)
```

Le due chiamate hanno lo stesso centro, la stessa mappa e lo stesso fog. Il
secondo risultato è quindi byte-per-byte identico al primo.

Per ogni tile percorso, il codice esegue attualmente:

```text
2.048 byte di memset WRAM
1.024 byte trasferiti in VRAM
due compositing completi identici
```

Le API GBDK rendono sicuro l'accesso alla VRAM, ma devono aspettare le fasi
compatibili del PPU; dimezzare le copie riduce direttamente gli stall:
[Pan Docs, Accessing VRAM and OAM](https://gbdev.io/pandocs/Accessing_VRAM_and_OAM.html).

## 4. Ridondanza strutturale dimostrata

È stata analizzata l'intera `tiles_map` generata, non soltanto il generatore.

Per tutti i quattro gruppi e tutte le 81 combinazioni della botola:

```text
stato TL modifica esclusivamente le posizioni 0 e 1
stato TR modifica esclusivamente le posizioni 2 e 3
stato BL modifica esclusivamente le posizioni 4 e 5
stato BR modifica esclusivamente le posizioni 6 e 7
```

La ricostruzione per angoli è risultata esatta per tutte le 324 varianti.

Per il pavimento:

```text
TL modifica soltanto 0–1
TR modifica soltanto 2–3
le posizioni 4–7 sono costanti per l'intero gruppo
```

Anche le 36 varianti del pavimento sono state ricostruite esattamente.

Questo consente la seguente fattorizzazione.

### Tabella pavimento

Per ogni gruppo:

```text
TL:     3 stati × 2 tile = 6 byte
TR:     3 stati × 2 tile = 6 byte
bottom: 4 tile costanti  = 4 byte
totale per gruppo       = 16 byte
4 gruppi                = 64 byte
```

### Tabella botola

Per ogni gruppo:

```text
4 angoli × 3 stati × 2 tile = 24 byte
4 gruppi                     = 96 byte
```

### Risultato

```text
tabella attuale:    2.884 byte
tabella fattorizzata: 160 byte
risparmio lordo:    2.724 byte
```

Il risparmio è ottenibile:

- mantenendo tutti i 151 tile;
- mantenendo scacchiera e penombra;
- senza cambiare il risultato grafico;
- senza compressione o decompressione;
- con accesso casuale diretto.

L'asset completo scenderebbe indicativamente da 5.364 a 2.640 byte, una
riduzione del **50,8%**. Considerando un piccolo aumento di codice, il guadagno
netto prevedibile è circa 2,5–2,7 KiB. Il margine ROM della main build
passerebbe da circa 3,1 KiB a quasi 5,8 KiB.

## 5. Ottimizzazioni raccomandate

### A. Eliminare il secondo `draw_map()` del passo

Priorità: **massima**; rischio: **basso**; beneficio: circa **50% del lavoro di
tiling durante il movimento**.

Mantenere il redraw a metà passo preserva l'effetto attuale del fog. A
completamento bastano snap camera e aggiornamento sprite.

Prima della modifica va aggiunto un test che confronti `map_buffer` dopo le due
chiamate per cammino, corsa e salto. Per il codice corrente il contenuto è
deterministicamente uguale.

### B. Sostituire `tiles_map` con tabelle per angolo

Priorità: **massima**; rischio: **medio-basso**; beneficio: **2.724 byte ROM
lordi**.

Layout possibile:

```c
// group = (is_dark << 1) | is_alt
const uint8_t floor_parts[4][16];
const uint8_t hatch_parts[4][24];
```

Il renderer copia direttamente quattro coppie:

```text
pair 0 ← TL[state_tl]
pair 1 ← TR[state_tr]
pair 2 ← BL[state_bl] o bottom costante
pair 3 ← BR[state_br] o bottom costante
```

Il PNG esaustivo può continuare a essere usato come sorgente/verifica.
`png2asset -map -tiles_only` è stato provato sul file corrente: conserva
esattamente i 151 tile e omette la macro-map. Un passo Python deve poi generare
le due tabelle compatte in modo deterministico.

### C. Disegnare la botola usando `stairs_lx/stairs_ly`

Priorità: **media**; rischio: **basso**.

La seconda passata scansiona fino a 25 celle per trovare un solo elemento, ma
le coordinate della botola sono già globali. È sufficiente:

1. verificare se `stairs_lx/ly` è entro il fog;
2. calcolare distanza e gruppo;
3. disegnare una sola macro-cella.

Si conserva il comportamento “botola sempre sopra” evitando il secondo doppio
loop.

### D. Ridurre il rettangolo trasferito in VRAM

Priorità: **alta dopo A/B**; rischio: **medio**.

Il rettangolo geometrico massimo del fog è:

| Fog | Nuova area | Unione dopo passo di 1 tile | Unione dopo salto |
|---:|---:|---:|---:|
| radius 2 | 20×10 = 200 B | 22×11 = 242 B | 24×12 = 288 B |
| radius 1 | 12×6 = 72 B | 14×7 = 98 B | 16×8 = 128 B |

Il flush attuale è sempre 32×16 = 512 byte.

Per usare rettangoli più piccoli bisogna:

- azzerare l'intera BG map una volta entrando nel gameplay;
- conservare il bounding box precedente;
- pulire e trasferire l'unione vecchio/nuovo;
- gestire wrap X e Y, con fino a quattro sottorettangoli.

Non basta trasferire soltanto il nuovo bounding box: resterebbero tile vecchi
ai bordi quando il fog si sposta.

### E. Ridurre il `memset`

Priorità: **media**; rischio: **medio**.

Dopo l'introduzione del dirty rectangle, azzerare soltanto l'unione vecchio /
nuovo invece dei 1.024 byte completi. Farlo prima del dirty flush: ottimizzare
solo il `memset`, mantenendo un flush da 512 byte, offre un beneficio minore.

### F. Micro-ottimizzazioni

Priorità: **bassa**

- sostituire `(lx + ly) % 2` con `(lx + ly) & 1`, dato che le coordinate sono
  non negative;
- rinominare `mask` in `ternary_index` finché esiste la codifica base 3;
- eliminare `uint16_t mask` dalla botola dopo la fattorizzazione;
- valutare l'inlining o una piccola cache 5×5 per `get_tile_state()`;
- scrivere le quattro coppie direttamente invece dei loop 2×4, misurando però
  l'aumento di codice.

Queste modifiche non devono precedere A e B: incidono molto meno.

## 6. Alternative con compromessi grafici

### Eliminare la scacchiera

Conservando solo i gruppi chiaro A e scuro A:

```text
tile pavimento: 62 → 32
tile botola:     88 → 48
tile totali:    151 → circa 81
risparmio tile data: circa 1.120 byte
```

Anche le tabelle fattorizzate scenderebbero da 160 a 80 byte.

È un risparmio importante e libera indici VRAM, ma il pavimento diventerebbe
più uniforme. Non è raccomandato come prima scelta, perché la fattorizzazione
recupera già più ROM senza perdita visiva.

### Ridurre gli stati da tre a due

Trattare ogni vicino come presente/assente ridurrebbe le combinazioni, ma
perderebbe il raccordo fra pavimento chiaro e penombra. Su DMG non esiste una
palette per tile alternativa che possa recuperare l'effetto. Scelta
sconsigliata.

### Integrare la botola nel painter's algorithm

Disegnando la botola nella passata normale, le celle a sud/est potrebbero
coprirne i raccordi inferiori. In teoria basterebbero così TL e TR, riducendo
tile e tabelle.

Il rischio è che il pavimento successivo copra parti importanti del disegno
della botola. Va valutato soltanto tramite prototipo e confronto pixel, non come
ottimizzazione immediata.

### Generare tile dinamicamente

Comporre corner tile e trasferirli in VRAM a runtime risparmierebbe ROM, ma
aggiungerebbe scritture VRAM, gestione cache e possibili stall. La tabella
fattorizzata ottiene quasi lo stesso vantaggio con complessità molto minore.

### Comprimere `tiles_map`

Una compressione RLE/ZX0 riduce lo spazio, ma elimina l'accesso casuale:
bisognerebbe decomprimere 2.884 byte in RAM o per ogni redraw. La
fattorizzazione è più piccola, immediatamente indicizzabile e non richiede un
buffer.

## 7. Piano di implementazione sicuro

### Fase 1 — test di equivalenza host

Creare un test che:

1. legga le 360 varianti attuali;
2. generi `floor_parts` e `hatch_parts`;
3. ricostruisca ogni variante;
4. confronti gli otto indici originali;
5. fallisca alla prima differenza.

Questo test ha già dato equivalenza completa durante l'audit; va reso
permanente.

### Fase 2 — rimozione redraw duplicato

1. salvare screenshot di cammino, corsa, salto e wrap;
2. rimuovere il redraw al completamento;
3. ripetere screenshot e test di stato;
4. verificare morte durante un passo e arrivo sulla botola.

### Fase 3 — asset compatto

1. usare l'export `-tiles_only`;
2. generare le tabelle compatte;
3. sostituire gli accessi `tiles_map[4 + v*8 + ...]`;
4. confrontare screenshot pixel-perfect;
5. misurare `.map`, dimensione ROM e numero tile.

### Fase 4 — dirty rectangle

1. pulizia completa della BG map entrando nel gameplay;
2. bounding box senza wrap;
3. test dei quattro bordi;
4. wrap X, wrap Y e wrap simultaneo;
5. test radius 1 e salti da due celle.

## 8. Conclusione

Il sistema di tiling non va sostituito: **la logica grafica è valida e adatta
al Game Boy**. Va invece cambiato il modo in cui le combinazioni vengono
archiviate e trasferite.

Le due ottimizzazioni migliori sono indipendenti e senza perdita estetica:

1. un solo redraw per passo;
2. lookup per angolo da 160 byte al posto della macro-map da 2.884 byte.

Insieme offrono il maggiore beneficio possibile con rischio contenuto:
circa 2,5–2,7 KiB ROM recuperati e dimezzamento del lavoro di tiling durante il
movimento. Solo dopo conviene affrontare dirty rectangles o semplificazioni
grafiche.
