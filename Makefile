GBDK_HOME = /home/enne2/.local/gbdk
LCC = $(GBDK_HOME)/bin/lcc
PNG2ASSET = $(GBDK_HOME)/bin/png2asset

# Source and build directories
SRC_DIR = src
ASSETS_DIR = assets
SCRIPTS_DIR = scripts
BUILD_DIR = build

# C source files
SRCS = $(SRC_DIR)/main.c $(SRC_DIR)/engine.c $(SRC_DIR)/globals.c $(SRC_DIR)/maze.c $(SRC_DIR)/sound.c $(SRC_DIR)/render.c $(SRC_DIR)/player_logic.c $(SRC_DIR)/enemy_logic.c $(SRC_DIR)/tiles.c $(SRC_DIR)/player.c $(SRC_DIR)/enemy.c $(SRC_DIR)/gameover.c $(SRC_DIR)/stamina.c $(SRC_DIR)/level.c $(SRC_DIR)/title_bg.c $(SRC_DIR)/screens/screens.c $(SRC_DIR)/screens/instructions.c $(SRC_DIR)/screens/death.c $(SRC_DIR)/screens/going_deeper.c $(SRC_DIR)/screens/finale.c

all: $(BUILD_DIR)/hello_iso.gb $(BUILD_DIR)/test_gameover.gb $(BUILD_DIR)/test_finale.gb

# Generate image assets
generate_images: $(SCRIPTS_DIR)/generate_assets.py $(SCRIPTS_DIR)/generate_enemy.py $(SCRIPTS_DIR)/generate_level.py
	cd $(ASSETS_DIR) && python3 ../$(SCRIPTS_DIR)/generate_assets.py
	cd $(ASSETS_DIR) && python3 ../$(SCRIPTS_DIR)/generate_enemy.py
	cd $(ASSETS_DIR) && python3 ../$(SCRIPTS_DIR)/generate_level.py

# Convert image assets to C source files
generate_c_assets: generate_images
	$(PNG2ASSET) $(ASSETS_DIR)/tiles.png -c $(SRC_DIR)/tiles.c -map -bpp 2 -noflip -keep_palette_order
	$(PNG2ASSET) $(ASSETS_DIR)/player.png -c $(SRC_DIR)/player.c -sw 16 -sh 16 -bpp 2 -noflip -keep_palette_order
	$(PNG2ASSET) $(ASSETS_DIR)/enemy.png -c $(SRC_DIR)/enemy.c -sw 16 -sh 16 -bpp 2 -noflip -keep_palette_order -sp 0x10
	$(PNG2ASSET) $(ASSETS_DIR)/gameover.png -c $(SRC_DIR)/gameover.c -bpp 2 -noflip -keep_palette_order
	$(PNG2ASSET) $(ASSETS_DIR)/next_level.png -c $(SRC_DIR)/next_level.c -map -bpp 2 -noflip -max_palettes 1
	$(PNG2ASSET) $(ASSETS_DIR)/stamina.png -c $(SRC_DIR)/stamina.c -bpp 2 -noflip -keep_palette_order
	$(PNG2ASSET) $(ASSETS_DIR)/level.png -c $(SRC_DIR)/level.c -sw 8 -sh 16 -bpp 2 -noflip -keep_palette_order -keep_duplicate_tiles
	$(PNG2ASSET) $(ASSETS_DIR)/title_bg.png -c $(SRC_DIR)/title_bg.c $(SRC_DIR)/screens/screens.c $(SRC_DIR)/screens/instructions.c $(SRC_DIR)/screens/death.c $(SRC_DIR)/screens/going_deeper.c $(SRC_DIR)/screens/finale.c -map -bpp 2 -noflip -keep_palette_order -max_palettes 1

# Main ROM target
$(BUILD_DIR)/hello_iso.gb: generate_c_assets $(SRCS)
	mkdir -p $(BUILD_DIR)
	$(LCC) $(LCCFLAGS) -o $(BUILD_DIR)/hello_iso.gb $(SRCS)

# Test ROM target
$(BUILD_DIR)/test_gameover.gb: generate_c_assets $(SRC_DIR)/test_gameover_render.c
	mkdir -p $(BUILD_DIR)
	$(LCC) -Wa-l -Wl-m -Wl-j -o $(BUILD_DIR)/test_gameover.gb $(SRC_DIR)/test_gameover_render.c $(SRC_DIR)/player.c $(SRC_DIR)/enemy.c $(SRC_DIR)/gameover.c $(SRC_DIR)/stamina.c

$(BUILD_DIR)/test_finale.gb: $(SRC_DIR)/test_finale_render.c
	mkdir -p $(BUILD_DIR)
	$(LCC) -Wa-l -Wl-m -Wl-j -o $(BUILD_DIR)/test_finale.gb $(SRC_DIR)/test_finale_render.c $(SRC_DIR)/globals.c $(SRC_DIR)/sound.c

clean:
	rm -rf $(BUILD_DIR)/*
	rm -f $(SRC_DIR)/tiles.c $(SRC_DIR)/tiles.h
	rm -f $(SRC_DIR)/player.c $(SRC_DIR)/player.h
	rm -f $(SRC_DIR)/enemy.c $(SRC_DIR)/enemy.h
	rm -f $(SRC_DIR)/gameover.c $(SRC_DIR)/gameover.h
	rm -f $(SRC_DIR)/stamina.c $(SRC_DIR)/stamina.h
	rm -f $(SRC_DIR)/level.c $(SRC_DIR)/level.h
	rm -f $(SRC_DIR)/title_bg.c $(SRC_DIR)/screens/screens.c $(SRC_DIR)/screens/instructions.c $(SRC_DIR)/screens/death.c $(SRC_DIR)/screens/going_deeper.c $(SRC_DIR)/screens/finale.c $(SRC_DIR)/title_bg.h
