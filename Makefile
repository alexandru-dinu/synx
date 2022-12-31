INPUT=

.PHONY: run
run: main.py
	python3 $< --input-file $(INPUT)

# list TODOs
.PHONY: todos
todos:
	@grep --color=auto -Hn -E '^(.*)TODO:(.*)$$' *.py
