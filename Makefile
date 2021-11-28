
################################################################################
# Main Tasks

# Initialize the project. The first step after cloning the repo.
init:
	poetry install

# Runs the app in production mode.
run:
	poetry run python -O ./agents_playground/main.py --log ERROR

# Development run target. Runs breakpoint statements, asserts and the @timer decorator. 
# Will leverage PDB if there are any breakpoints.
dev:
	poetry run python -X dev ./agents_playground/main.py --log DEBUG

# Run unit tests. Includes all files in ./test named test_*.py and *_test.py.
test:
	poetry run pytest

# Perform static type checking on the project.
check:
	poetry run mypy --config-file mypy.ini agents_playground

# Launches pudb debugger in the terminal if there are any breakpoints. 
debug:
	PYTHONBREAKPOINT="pudb.set_trace" poetry run python -X dev ./agents_playground/main.py --log DEBUG

# Launch's py-spy profiler and generates an interactive flame graph.
flame:
	sudo poetry run py-spy record -o profile.svg -- python -X dev ./agents_playground/main.py --log DEBUG

top:
	sudo poetry run py-spy top -- python -X dev ./agents_playground/main.py --log DEBUG
