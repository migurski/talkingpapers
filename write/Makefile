all: FPDF
	#

FPDF:
	curl -sL "http://www.fpdf.org/en/dl.php?v=16&f=tgz" > fpdf.tar.gz
	tar -xzf fpdf.tar.gz
	mv fpdf16 FPDF
	rm -f fpdf.tar.gz

clean:
	rm -rf FPDF
