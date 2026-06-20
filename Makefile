GBDK_HOME = /home/enne2/.local/gbdk
LCC = $(GBDK_HOME)/bin/lcc
PNG2ASSET = $(GBDK_HOME)/bin/png2asset

all: hello_iso.gb

assets: generate_assets.py
	python3 generate_assets.py
	$(PNG2ASSET) tiles.png -c tiles.c -map -bpp 2 -noflip -keep_palette_order
	$(PNG2ASSET) player.png -c player.c -sw 16 -sh 16 -bpp 2 -noflip -keep_palette_order

hello_iso.gb: assets main.c engine.c
	$(LCC) -Wa-l -Wl-m -Wl-j -o hello_iso.gb main.c engine.c tiles.c player.c

clean:
	rm -f *.o *.lst *.map *.gb *.ihx *.sym *.cdb *.adb *.asm
