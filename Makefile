.PHONY: run tests

run:
	uv run v-inject

tests:
	uv run pytest