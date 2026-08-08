# Script legacy (archivio conservativo)

Script non referenziati dalla build, conservati per consultazione storica.
Nessuno di questi viene invocato da `make`; la pipeline supportata è descritta
in `scripts/README.md`.

## Sottocartelle

- `unsafe_rewriters/` — snapshot storici che riscrivevano i sorgenti con
  sostituzioni testuali. **Non eseguire sul codice corrente** (vedi il loro
  README interno).
- `obsolete_tests/` — vecchi runner PyBoy/OpenCV con API o percorsi superati.
  La suite supportata è `make test`.
- `peasant_experiments/` — generatori del personaggio (peasant/ghost) in varie
  iterazioni, superati da `generate_assets.py` + `generate_enemy.py`.
- `image_analysis/` — script di analisi colore/luminosità e centraggio usati
  durante lo sviluppo degli asset.
- `cartridge/` — generazione e verifica delle copertine cartuccia (materiale
  stampa, non parte della ROM).
- `asset_experiments/` — esperimenti su singoli asset (level UI, victory,
  next_level) non integrati nella pipeline.
- `audio/` — rendering WAV della musica del finale e test musicali; la musica
  del finale è archiviata esternamente e non compilata nella ROM.
