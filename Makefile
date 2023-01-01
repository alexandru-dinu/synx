SRC := $(shell find {synx,tests} -name "*.py")

.PHONY: test
test:
	@poetry run pytest -vv --exitfirst

.PHONY: format
format:
	@poetry run autoflake --remove-all-unused-imports -i $(SRC)
	@poetry run isort $(SRC)
	@poetry run black $(SRC)

.PHONY: list-todo
list-todo:
	@grep --color=auto -Hn -E '^(.*)TODO:(.*)$$' *.py
