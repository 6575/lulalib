.PHONY: tests build

tests:
	poetry run pytest tests/ -v --tb=short -s

build: tests
	poetry build

