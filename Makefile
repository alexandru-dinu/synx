# list TODOs
.PHONY: todos
todos:
	@grep --color=auto -Hn -E '^(.*)TODO:(.*)$$' *.py
