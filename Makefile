INPUT=

.PHONY: run
run: main.py
	python3 $< --input-file $(INPUT)
