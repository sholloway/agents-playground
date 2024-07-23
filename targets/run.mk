# Runs the app in production mode.
# Typical development flow is:
# make check test run
run:
	@( \
	source .venv/bin/activate; \
	poetry run python -O agents_playground --log ERROR; \
	)

# Run the app with a sim already selected. 
run_sim:
	@( \
	source .venv/bin/activate; \
	poetry run python -O agents_playground --log ERROR --sim ~/Documents/my_simulation; \
	)

# Run the app with the old UI. 
run_classic:
	@( \
	source .venv/bin/activate; \
	poetry run python -O agents_playground --log ERROR --ui_version CLASSIC; \
	)

# Development run target. Runs breakpoint statements, asserts and the @timer decorator. 
# Will leverage PDB if there are any breakpoints.
dev:
	@( \
	source .venv/bin/activate; \
	poetry run python -X dev agents_playground --log DEBUG; \
	)
