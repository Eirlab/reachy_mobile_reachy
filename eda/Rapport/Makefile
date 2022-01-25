TEXCOMPILER=pdflatex
TEXFLAGS=-output-directory=$(OUTPUT_DIR) -interaction=nonstopmode

OUTPUT_DIR=output/
FILE=report
LATEX_TMP_FILES=*.log *.pdf *.aux *.synctex.gz *.acn *.bcf *.glo *.ist *.out *.ptc *.run.xml *.blg *.toc *.bbl tags.*

BIB=bibtex
BIBLIOGRAPHY=bibliography/bibliography.bib

#USE_BIB = yes|no
USE_BIB?=no




ifeq ($(USE_BIB),yes)
	ALL=bib
else
	ALL=compile
endif


all:
	$(MAKE) $(ALL)
	cp $(OUTPUT_DIR)$(FILE).pdf .
	
compile:
	mkdir -p $(OUTPUT_DIR)
	$(TEXCOMPILER) $(TEXFLAGS) $(FILE).tex

bib:
	$(MAKE) compile
	$(BIB) $(OUTPUT_DIR)$(FILE)
	$(MAKE) compile
	
clean:
	rm -rf $(OUTPUT_DIR) $(LATEX_TMP_FILES)
