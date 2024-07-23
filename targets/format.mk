# Format the codebase
format:
	@( \
	source .venv/bin/activate; \
	poetry run black agents_playground/; \
	)

# Format the tests.
format_tests:
	@( \
	source .venv/bin/activate; \
	poetry run black tests/; \
	)