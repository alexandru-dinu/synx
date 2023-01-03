SRC := $(shell find {synx,tests} -name "*.py")

.PHONY: test
test:
	@poetry run pytest -vv --exitfirst

.PHONY: typecheck
typecheck:
	@poetry run mypy synx/

.PHONY: format
format:
	@poetry run autoflake --remove-all-unused-imports -i $(SRC)
	@poetry run isort $(SRC)
	@poetry run black $(SRC)

.PHONY: list-todo
list-todo:
	@grep --color=auto -Hn -E '^(.*)TODO:(.*)$$' $(SRC)

.PHONY: clean
clean:
	rm -rf **/__pycache__
	rm -rf **/.ipynb_checkpoints
	rm -rf .mypy_cache
	rm -rf .hypothesis
	rm -rf .pytest_cache
