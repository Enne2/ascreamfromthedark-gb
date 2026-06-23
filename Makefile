GBDK_HOME = /home/enne2/.local/gbdk
LCC = $(GBDK_HOME)/bin/lcc
PNG2ASSET = $(GBDK_HOME)/bin/png2asset

all: hello_iso.gb test_gameover.gb

assets: generate_assets.py
	python3 generate_assets.py
	$(PNG2ASSET) tiles.png -c tiles.c -map -bpp 2 -noflip -keep_palette_order
	$(PNG2ASSET) player.png -c player.c -sw 16 -sh 16 -bpp 2 -noflip -keep_palette_order
	$(PNG2ASSET) gameover.png -c gameover.c -bpp 2 -noflip -keep_palette_order
	$(PNG2ASSET) stamina.png -c stamina.c -bpp 2 -noflip -keep_palette_order

	$(PNG2ASSET) title_bg.png -c title_bg.c -map -bpp 2 -noflip -keep_palette_order -max_palettes 1

hello_iso.gb: assets main.c engine.c
	$(LCC) -Wa-l -Wl-m -Wl-j -o hello_iso.gb main.c engine.c tiles.c player.c gameover.c stamina.c title_bg.c

test_gameover.gb: assets test_gameover_render.c
	$(LCC) -Wa-l -Wl-m -Wl-j -o test_gameover.gb test_gameover_render.c player.c gameover.c stamina.c

clean:
	rm -f *.o *.lst *.map *.gb *.ihx *.sym *.cdb *.adb *.asm gameover.c gameover.h gameover.png player.png tiles.png player.c player.h tiles.c tiles.h test_gameover_render.o player.o gameover.o stamina.c stamina.h stamina.png stamina.o title_bg.c title_bg.h title_bg.o



