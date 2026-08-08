GBDK_HOME ?= $(HOME)/.local/gbdk
LCC ?= $(GBDK_HOME)/bin/lcc
PNG2ASSET ?= $(GBDK_HOME)/bin/png2asset
PYTHON ?= python3
ROM_TITLE ?= A SCREAM DARK
LCCFLAGS ?= -Wa-l -Wl-m -Wl-j -Wm-yn"$(ROM_TITLE)" -Wm-yj

# Source and build directories
SRC_DIR = src
ASSETS_DIR = assets
SCRIPTS_DIR = scripts
BUILD_DIR = build

.PHONY: all clean assets generate_images generate_c_assets test

# C source files
SRCS = $(SRC_DIR)/main.c $(SRC_DIR)/engine.c $(SRC_DIR)/globals.c $(SRC_DIR)/maze.c $(SRC_DIR)/sound.c $(SRC_DIR)/render.c $(SRC_DIR)/player_logic.c $(SRC_DIR)/enemy_logic.c $(SRC_DIR)/tiles.c $(SRC_DIR)/tiling_parts.c $(SRC_DIR)/player.c $(SRC_DIR)/enemy.c $(SRC_DIR)/gameover.c $(SRC_DIR)/stamina.c $(SRC_DIR)/level.c $(SRC_DIR)/title_bg.c $(SRC_DIR)/screens/screens.c $(SRC_DIR)/screens/instructions.c $(SRC_DIR)/screens/death.c $(SRC_DIR)/screens/going_deeper.c $(SRC_DIR)/screens/finale.c $(SRC_DIR)/screens/credits.c $(SRC_DIR)/screens/intro.c

all: $(BUILD_DIR)/hello_iso.gb $(BUILD_DIR)/test_gameover.gb $(BUILD_DIR)/test_finale.gb

# Asset C files are versioned build inputs. Regeneration is explicit so a
# normal build never rewrites the working tree as a side effect.
assets: generate_c_assets

# Rename the main ROM to match the game title
release: all
	cp $(BUILD_DIR)/hello_iso.gb $(BUILD_DIR)/"AScreamFromTheDark.gb"

# Generate image assets
generate_images: $(SCRIPTS_DIR)/generate_assets.py $(SCRIPTS_DIR)/generate_enemy.py $(SCRIPTS_DIR)/generate_level.py $(SCRIPTS_DIR)/generate_tiling_parts.py
	cd $(ASSETS_DIR) && $(PYTHON) ../$(SCRIPTS_DIR)/generate_assets.py
	cd $(ASSETS_DIR) && $(PYTHON) ../$(SCRIPTS_DIR)/generate_enemy.py
	cd $(ASSETS_DIR) && $(PYTHON) ../$(SCRIPTS_DIR)/generate_level.py
	$(PYTHON) $(SCRIPTS_DIR)/generate_tiling_parts.py

# Convert image assets to C source files
generate_c_assets: generate_images
	$(PNG2ASSET) $(ASSETS_DIR)/tiles.png -c $(SRC_DIR)/tiles.c -map -tiles_only -bpp 2 -noflip -keep_palette_order
	$(PNG2ASSET) $(ASSETS_DIR)/player.png -c $(SRC_DIR)/player.c -sw 16 -sh 16 -bpp 2 -noflip -keep_palette_order
	$(PNG2ASSET) $(ASSETS_DIR)/enemy.png -c $(SRC_DIR)/enemy.c -sw 16 -sh 16 -bpp 2 -noflip -keep_palette_order -sp 0x10
	$(PNG2ASSET) $(ASSETS_DIR)/gameover.png -c $(SRC_DIR)/gameover.c -bpp 2 -noflip -keep_palette_order
	$(PNG2ASSET) $(ASSETS_DIR)/next_level.png -c $(SRC_DIR)/next_level.c -map -bpp 2 -noflip -max_palettes 1
	$(PNG2ASSET) $(ASSETS_DIR)/stamina.png -c $(SRC_DIR)/stamina.c -bpp 2 -noflip -keep_palette_order
	$(PNG2ASSET) $(ASSETS_DIR)/level.png -c $(SRC_DIR)/level.c -sw 8 -sh 16 -bpp 2 -noflip -keep_palette_order -keep_duplicate_tiles
	$(PNG2ASSET) $(ASSETS_DIR)/title_bg.png -c $(SRC_DIR)/title_bg.c -map -bpp 2 -noflip -keep_palette_order -max_palettes 1

# Main ROM target
$(BUILD_DIR)/hello_iso.gb: $(SRCS)
	mkdir -p $(BUILD_DIR)
	$(LCC) $(LCCFLAGS) -o $(BUILD_DIR)/hello_iso.gb $(SRCS)

# Test ROM target
$(BUILD_DIR)/test_gameover.gb: $(SRC_DIR)/test_gameover_render.c $(SRC_DIR)/player.c $(SRC_DIR)/enemy.c $(SRC_DIR)/gameover.c $(SRC_DIR)/stamina.c
	mkdir -p $(BUILD_DIR)
	$(LCC) -Wa-l -Wl-m -Wl-j -o $(BUILD_DIR)/test_gameover.gb $(SRC_DIR)/test_gameover_render.c $(SRC_DIR)/player.c $(SRC_DIR)/enemy.c $(SRC_DIR)/gameover.c $(SRC_DIR)/stamina.c

$(BUILD_DIR)/test_finale.gb: $(SRC_DIR)/test_finale_render.c
	mkdir -p $(BUILD_DIR)
	$(LCC) -Wa-l -Wl-m -Wl-j -o $(BUILD_DIR)/test_finale.gb $(SRC_DIR)/test_finale_render.c $(SRC_DIR)/globals.c $(SRC_DIR)/sound.c

clean:
	rm -rf $(BUILD_DIR)/*

test: $(BUILD_DIR)/hello_iso.gb
	$(PYTHON) $(SCRIPTS_DIR)/validate_rom_header.py $< --title "$(ROM_TITLE)"
	$(PYTHON) $(SCRIPTS_DIR)/validate_tiling_visual.py $< $(BUILD_DIR)/hello_iso.noi $(BUILD_DIR)/test-artifacts/floor.png --scenario floor
	$(PYTHON) $(SCRIPTS_DIR)/validate_tiling_visual.py $< $(BUILD_DIR)/hello_iso.noi $(BUILD_DIR)/test-artifacts/hatch.png --scenario hatch
	$(PYTHON) $(SCRIPTS_DIR)/validate_tiling_visual.py $< $(BUILD_DIR)/hello_iso.noi $(BUILD_DIR)/test-artifacts/wrap_x.png --scenario wrap_x
	$(PYTHON) $(SCRIPTS_DIR)/validate_tiling_visual.py $< $(BUILD_DIR)/hello_iso.noi $(BUILD_DIR)/test-artifacts/wrap_y.png --scenario wrap_y
	$(PYTHON) $(SCRIPTS_DIR)/validate_tiling_visual.py $< $(BUILD_DIR)/hello_iso.noi $(BUILD_DIR)/test-artifacts/stamina_0.png --scenario floor --stamina 0
	$(PYTHON) $(SCRIPTS_DIR)/validate_tiling_visual.py $< $(BUILD_DIR)/hello_iso.noi $(BUILD_DIR)/test-artifacts/stamina_50.png --scenario floor --stamina 50
	$(PYTHON) $(SCRIPTS_DIR)/validate_tiling_visual.py $< $(BUILD_DIR)/hello_iso.noi $(BUILD_DIR)/test-artifacts/stamina_100.png --scenario floor --stamina 100
	$(PYTHON) $(SCRIPTS_DIR)/validate_static_screen.py $< $(BUILD_DIR)/hello_iso.noi $(BUILD_DIR)/test-artifacts/title.png --screen title
	$(PYTHON) $(SCRIPTS_DIR)/validate_static_screen.py $< $(BUILD_DIR)/hello_iso.noi $(BUILD_DIR)/test-artifacts/intro.png --screen intro
	$(PYTHON) $(SCRIPTS_DIR)/validate_static_screen.py $< $(BUILD_DIR)/hello_iso.noi $(BUILD_DIR)/test-artifacts/credits.png --screen credits
	$(PYTHON) $(SCRIPTS_DIR)/validate_static_screen.py $< $(BUILD_DIR)/hello_iso.noi $(BUILD_DIR)/test-artifacts/instructions.png --screen instructions
	$(PYTHON) $(SCRIPTS_DIR)/validate_static_screen.py $< $(BUILD_DIR)/hello_iso.noi $(BUILD_DIR)/test-artifacts/death.png --screen death
	$(PYTHON) $(SCRIPTS_DIR)/validate_static_screen.py $< $(BUILD_DIR)/hello_iso.noi $(BUILD_DIR)/test-artifacts/deeper.png --screen deeper
	$(PYTHON) $(SCRIPTS_DIR)/validate_static_screen.py $< $(BUILD_DIR)/hello_iso.noi $(BUILD_DIR)/test-artifacts/finale.png --screen finale
