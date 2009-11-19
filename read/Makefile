all: out.png
	#

out.png: layout.pgm layout.sift GMDH02_00647.pgm GMDH02_00647.sift
	python matchup.py layout.pgm layout.sift GMDH02_00647.pgm GMDH02_00647.sift

GMDH02_00647.sift: bin GMDH02_00647.pgm
	bin/sift --peak-thresh=8 -o GMDH02_00647.sift GMDH02_00647.pgm

GMDH02_00647.pgm: GMDH02_00647.png
	convert -geometry 1000x1000 GMDH02_00647.png GMDH02_00647.pgm

GMDH02_00364.sift: bin GMDH02_00364.pgm
	bin/sift --peak-thresh=8 -o GMDH02_00364.sift GMDH02_00364.pgm

GMDH02_00364.pgm: GMDH02_00364.png
	convert -geometry 1000x1000 GMDH02_00364.png GMDH02_00364.pgm

layout.sift: bin layout.pgm
	bin/sift --peak-thresh=8 -o layout.sift layout.pgm

layout.pgm: layout.png
	convert -geometry 1000x1000 layout.png layout.pgm

bin:
	curl -O http://www.vlfeat.org/download/vlfeat-0.9.3-bin.tar.gz
	tar -xzf vlfeat-0.9.3-bin.tar.gz
	mv vlfeat/bin/mac bin
	rm -rf vlfeat vlfeat-0.9.3-bin.tar.gz

clean:
	rm -rf bin
	rm -f *.pgm *.sift out.png
