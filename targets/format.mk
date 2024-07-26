# Format the codebase
run-format:
	@( \
	source .venv/bin/activate; \
	poetry run black agents_playground/; \
	)

# Format the tests.
run-format-tests:
	@( \
	source .venv/bin/activate; \
	poetry run black tests/; \
	)