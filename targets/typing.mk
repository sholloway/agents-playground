# Perform static type checking on the project.
run-check:
	poetry run mypy --check-untyped-defs --config-file mypy.ini agents_playground