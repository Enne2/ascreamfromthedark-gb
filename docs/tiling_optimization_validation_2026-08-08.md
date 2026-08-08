# Ottimizzazione tiling: implementazione e validazione visiva

- Data: **8 agosto 2026**
- Target: **Game Boy DMG/CGB, ROM 32 KiB, GBDK-2020/SDCC**
- Obiettivo: ridurre ROM e lavoro del renderer senza modificare l'estetica
- Esito: **quattro fasi accettate con confronto pixel-perfect**

## Risultato

L'aspetto del pavimento, della penombra e della botola è rimasto invariato.
Le ottimizzazioni intervengono solo sulla rappresentazione degli indici e sulla
quantità di lavoro ripetuto o trasferito in VRAM.

| Misura | Baseline | Finale | Differenza |
|---|---:|---:|---:|
| ROM `_CODE + _HOME` | 28.988 B | 26.631 B | **-2.357 B (-8,1%)** |
| Lookup delle varianti | 2.884 B | 160 B | **-2.724 B (-94,5%)** |
| `draw_map()` per passo | 2 | 1 | **-50%** |
| Flush VRAM, fog raggio 2 | 1.024 B/passo | fino a 242 B/passo | **-76,4%** |
| Flush VRAM, fog raggio 1 | 1.024 B/passo | fino a 98 B/passo | **-90,4%** |
| WRAM statica | 2.708 B | 2.721 B | +13 B |

Il file ROM resta necessariamente di 32 KiB; il risparmio è spazio libero
interno. Il nuovo dirty rectangle aggiunge codice, quindi il guadagno ROM netto
è inferiore ai 2.724 byte eliminati dalla tabella, ma resta pari a 2.357 byte.

## Fasi applicate

### 1. Eliminazione del ridisegno duplicato

Il fog veniva ricomposto a metà movimento usando la destinazione e nuovamente
alla fine con lo stesso centro. La seconda chiamata è stata rimossa. Il momento
in cui il giocatore vede l'aggiornamento non cambia.

### 2. Fattorizzazione esatta delle varianti

Le 360 macro-varianti 4x2 non sono più memorizzate integralmente. Il renderer
ricompone gli stessi otto indici usando parti indipendenti:

- pavimento: 4 gruppi x 16 byte = 64 byte;
- botola: 4 gruppi x 24 byte = 96 byte.

`scripts/generate_tiling_parts.py` ricostruisce e confronta esaustivamente tutte
le 360 varianti prima di scrivere i file C. La pipeline usa `png2asset
-tiles_only`, conservando identico il tileset grafico da 151 tile.

### 3. Accesso diretto alla botola

La seconda scansione dell'intera finestra del fog è stata sostituita con le
coordinate già note `stairs_lx/stairs_ly`. La botola continua a essere composta
per ultima, quindi il painter's order originale resta invariato.

### 4. Dirty rectangle VRAM con wrap

Il buffer 32x32 continua a essere composto nello stesso modo. In VRAM viene
trasferita soltanto l'unione fra i bounds isometrici precedenti e correnti:

- l'area nuova rende visibile il nuovo fog;
- l'area vecchia trasferisce gli zero necessari a cancellare il bordo uscente;
- il rettangolo viene diviso in massimo quattro segmenti quando attraversa il
  bordo circolare 32x32;
- un cambio livello invalida la cache e forza un unico full flush da 1.024 byte;
- un eventuale salto di coordinate superiore alla tilemap usa lo stesso fallback.

Per un passo interno, il rettangolo massimo è 22x11 tile con raggio 2 e 14x7
con raggio 1. Il costo una tantum del primo frame passa da 512 a 1.024 byte per
garantire che nessun residuo di titolo o livello precedente sopravviva.

## Gate eseguiti in ordine

Ogni test avvia la ROM in PyBoy, attraversa titolo/intro/istruzioni, inietta una
fixture deterministica nella vera WRAM, esegue movimenti reali e salva PNG più
stato JSON.

| Gate | Stato | Confronto baseline/finale |
|---|---|---:|
| Pavimento 7x7 | superato | 0 pixel differenti |
| Botola e raccordi | superato | 0 pixel differenti |
| Wrap X, 14 passi | superato | 0 pixel differenti |
| Wrap Y, 28 passi | superato | 0 pixel differenti |
| Trace di ogni passo X+Y | superato | **28/28 frame identici** |

Il primo tentativo della fase 4 è stato correttamente respinto: il puntatore
sorgente di `set_bkg_submap()` era pre-offsettato nonostante l'API applicasse già
`x,y`, producendo 3.034 pixel differenti. Dopo la correzione lo stesso gate è
stato ripetuto da zero ed è passato con differenza nulla.

Evidenze principali:

- `artifacts/tiling_validation/phase_04_gate_summary.png`: coppie
  baseline/finale per i quattro scenari;
- `artifacts/tiling_validation/phase_00_wrap_y_trace/`: 28 frame baseline;
- `artifacts/tiling_validation/phase_04_wrap_y_trace/`: 28 frame finali;
- file `.json` accanto alle schermate: coordinate finali, fixture e sequenza input.

## Verifiche tecniche

- build completa della ROM con GBDK riuscita;
- generatore: `Verified 360 exhaustive variants; wrote 160 compact lookup bytes`;
- script di test compilati con `py_compile`;
- hash SHA-256 identici per ciascuna delle quattro coppie finali;
- `git diff --check` pulito dopo la normalizzazione del file generato;
- restano solo warning SDCC preesistenti e non correlati.

## Limite residuo e prossimo passo possibile

`draw_map()` azzera ancora tutti i 1.024 byte di `map_buffer` a ogni
ricomposizione. È possibile ridurre anche questo costo cancellando soltanto i
bounds precedenti, ma il beneficio riguarda WRAM/CPU e richiede un'altra fase di
gate dedicata. Non è stato incluso qui per mantenere separata e verificabile la
modifica più rischiosa.
