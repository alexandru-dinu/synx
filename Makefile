INPUT=

.PHONY: run
run: main.py
	python3 $< --input-file $(INPUT) --max-depth 5

# list TODOs
.PHONY: todos
todos:
	@grep --color=auto -Hn -E '^(.*)TODO:(.*)$$' *.py
