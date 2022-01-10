################################################################################
# Main Tasks

# Initialize the project. The first step after cloning the repo.
init:
	poetry config virtualenvs.in-project true --local
	poetry install

# Runs the app in production mode.
run:
	poetry run python -O agents_playground --log ERROR

# Development run target. Runs breakpoint statements, asserts and the @timer decorator. 
# Will leverage PDB if there are any breakpoints.
dev:
	poetry run python -X dev agents_playground --log DEBUG

# Run unit tests. Includes all files in ./test named test_*.py and *_test.py.
test:
	poetry run pytest

# Perform static type checking on the project.
check:
	poetry run mypy --config-file mypy.ini agents_playground

# Launches pudb debugger in the terminal if there are any breakpoints. 
debug:
	PYTHONBREAKPOINT="pudb.set_trace" poetry run python -X dev agents_playground --log DEBUG

# Launch's py-spy profiler and generates an interactive flame graph.
# It then opens Speedcope in the browser. 
flame:
	sudo poetry run py-spy record \
		--output profile.speedscope.json \
		--threads \
		--rate 1000 \
		--format speedscope -- python -X dev agents_playground --log DEBUG
	
	speedscope ./profile.speedscope.json

# Display a running list of the top most expensive functions while the app is running.
top:
	sudo poetry run py-spy top -- python -X dev agents_playground --log DEBUG

# Launch an instance of the ptpython REPL in the Poetry venv.
shell:
	poetry run ptpython

# Launch an instance of bpython in the Poetry venv.
bshell:
	poetry run bpython

# Calculates code coverage.
cov:
	poetry run pytest --cov-report html --cov-report term --cov=agents_playground tests/
	open ./htmlcov/index.html

# Generates the code documentation.
doc:
	poetry run pdoc --html --force --output-dir ./pdocs agents_playground
	open ./pdocs/agents_playground/index.html