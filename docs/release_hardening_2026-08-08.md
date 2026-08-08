# Consolidamento release — 8 agosto 2026

## Esito

Sono stati completati i punti 1, 2, 4, 5 e 6 del triage successivo
all'ottimizzazione del tiling. La ROM finale compila da zero, supera la suite
headless e conserva pixel-identiche tutte le schermate confrontabili.

## 1. Stamina e layout VRAM

Il caricamento precedente richiedeva 52 tile da un array di 26 e usava la base
dispari 151 in modalità sprite 8x16. Il layout corretto è ora:

| Blocco | Base | Tile | Intervallo |
|---|---:|---:|---:|
| Background | 0 | 151 | 0–150 |
| Stamina | 152 | 26 | 152–177 |
| HUD livello | 178 | 22 | 178–199 |

Gate visivi esportati in `artifacts/stamina_validation/`:

- 0%: bordo vuoto;
- 50%: metà barra;
- 100%: barra piena;
- indicatore livello e gameplay integri.

## 2. Clean build sicura

`make clean` elimina soltanto gli output sotto `build/`; non cancella più
generatori C o sorgenti handwritten sotto `src/screens/`.

Verifica finale:

```text
make clean  -> PASS
make -j1    -> PASS (ROM principale + due ROM isolate)
```

## 4. Build e test riproducibili

- `GBDK_HOME`, `LCC`, `PNG2ASSET` e `PYTHON` sono sovrascrivibili;
- la build normale usa gli asset C versionati e non riscrive il working tree;
- `make assets` è la rigenerazione esplicita;
- `make test` è l'unico workflow supportato;
- runner PyBoy obsoleti non sono più presentati nel README.

La suite finale contiene 15 gate:

- header ROM e checksum;
- floor, hatch, wrap X, wrap Y;
- stamina 0/50/100;
- title, intro, credits, instructions, death, Going Deeper e finale.

## 5. Script legacy isolati

Nessun file è stato eliminato. Sono stati spostati e documentati:

- 10 riscrittori regex in `scripts/legacy/unsafe_rewriters/`;
- 5 runner obsoleti in `scripts/legacy/obsolete_tests/`.

Gli script attivi sono descritti in `scripts/README.md`.

## 6. Ottimizzazioni e header

### Clear WRAM incrementale

Il buffer 32x32 viene azzerato integralmente solo dopo invalidazione della
cache. Durante un passo viene pulito il solo rettangolo precedente:

| Fog | Prima | Dopo | Riduzione |
|---|---:|---:|---:|
| raggio 2 | 1.024 B | fino a 200 B | 80,5% |
| raggio 1 | 1.024 B | fino a 72 B | 93,0% |

La chiusura delle istruzioni invalida esplicitamente la cache perché quella
schermata riutilizza `map_buffer` per il testo. Gate: floor/hatch/wrap X tutti a
0 pixel di differenza; trace wrap Y 28/28 frame identici.

### Schermate statiche

Intro, crediti, istruzioni, morte, Going Deeper e finale trasferiscono la sola
area visibile 20x18 tramite submap con stride 32:

```text
1.024 -> 360 tile trasferiti (-64,8%)
```

Tutte le sei coppie baseline/finale hanno 0 pixel differenti. Il runner attende
il completamento reale del caricamento font e verifica che le tilemap non siano
vuote.

### Header cartuccia

La ROM contiene ora:

- titolo: `A SCREAM DARK`;
- destinazione: non-Giappone;
- tipo: ROM-only (`0x00`);
- dimensione: 32.768 byte;
- checksum header e globale verificati automaticamente.

Il titolo e il gameplay post-header sono pixel-identici alla baseline.

## Budget finale

| Sezione | Byte |
|---|---:|
| `_CODE` | 24.602 |
| `_HOME` | 2.377 |
| `_CODE + _HOME` | 26.979 |
| WRAM statica `_DATA` | 2.721 |

Rispetto alla baseline precedente a tutte le ottimizzazioni del tiling
(`28.988` byte ROM occupati), il risultato netto è **-2.009 byte (-6,9%)**,
pur includendo i nuovi helper di sicurezza e il clear incrementale.

## Residui

Restano warning SDCC già presenti (`title_update` e warning 110
dell'ottimizzatore). Non hanno bloccato build o test, ma possono essere ripuliti
in una fase separata. Il rischio hardware non affrontato in questo intervento è
il limite di dieci sprite per scanline con molti fantasmi visibili.
