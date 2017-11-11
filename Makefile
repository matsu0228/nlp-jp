NOUN_DIR=noun/
EXT_NOUN=python ./bin/extract_noun.py
# DAT=$(shell ls V*.)
# VTK=$(DAT:.dat=.vtk)

all:


noun.dic:
	# echo $(NOUN_DIR)$@
	$(EXT_NOUN) $(NOUN_DIR)$@

