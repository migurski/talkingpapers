all: out.png
	#

out.png: layout.pgm layout.sift fruit.pgm fruit.sift
	python matchup.py layout.pgm layout.sift fruit.pgm fruit.sift

layout.sift: bin layout.pgm
	bin/sift --peak-thresh=8 -o layout.sift layout.pgm

layout.pgm: layout.png
	convert -geometry 1000x1000 layout.png layout.pgm

fruit.sift: bin fruit.pgm
	bin/sift --peak-thresh=8 -o fruit.sift fruit.pgm

fruit.pgm: fruit.png
	convert fruit.png fruit.pgm

bin:
	curl -O http://www.vlfeat.org/download/vlfeat-0.9.3-bin.tar.gz
	tar -xzf vlfeat-0.9.3-bin.tar.gz
	mv vlfeat/bin/mac bin
	rm -rf vlfeat vlfeat-0.9.3-bin.tar.gz

clean:
	rm -rf bin
	rm -f *.pgm *.sift out.png
