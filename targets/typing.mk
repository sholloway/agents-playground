# Perform static type checking on the project.
check:
	poetry run mypy --check-untyped-defs --config-file mypy.ini agents_playground