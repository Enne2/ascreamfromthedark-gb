# Script attivi

## Build e asset

- `generate_assets.py`, `generate_enemy.py`, `generate_level.py`: sorgenti PNG;
- `generate_tiling_parts.py`: lookup compatto con verifica esaustiva;
- `make assets`: unica procedura supportata per rigenerare gli asset C.

## Test supportati

- `validate_tiling_visual.py`: runner deterministico PyBoy;
- `validate_static_screen.py`: regressione delle schermate testuali;
- `validate_rom_header.py`: metadati e checksum della cartuccia;
- `make test`: suite canonica della ROM principale.

## Storico

Tutti gli script non referenziati dalla build sono isolati in `legacy/`
(sottocartelle tematiche: `unsafe_rewriters/`, `obsolete_tests/`,
`peasant_experiments/`, `image_analysis/`, `cartridge/`,
`asset_experiments/`, `audio/`). Non fanno parte di alcun workflow
supportato e non vengono invocati dalla build.
