# Run cloc to measure the size of the project. This is installed via Nix.
#  Use cloc --progress=1 --exclude-dir=__pycache__ --by-file ./agents_playground
#  to see counts per file.
# https://github.com/AlDanial/cloc
size:
	@( \
	set -e ; \
	echo "Application Code"; \
	cloc --progress=1 --exclude-dir=__pycache__ ./agents_playground; \
	\
	echo "\nTest Code"; \
	cloc --progress=1 --exclude-dir=__pycache__ ./tests; \
	)

# Scan the codebase for antipatterns.
scan:
	@( \
	source .venv/bin/activate; \
	poetry run flake8 --select CE1, E2, E3, E4, E5, E7, E9, W1, W2, CR001 agents_playground/; \
	)