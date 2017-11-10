NOUN_DIR=noun/
EXT_NOUN=python ./bin/extract_noun.py

noun.dic:
	# echo $(NOUN_DIR)$@
	$(EXT_NOUN) $(NOUN_DIR)$@

