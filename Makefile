################################################################################
# Main Tasks

# Runs the app in production mode.
# Will be executed if you just run "make"
# Typical development flow is:
# make check test run
run:
	poetry run python -O agents_playground --log ERROR

# Initialize the project. The first step after cloning the repo.
# This only needs to be done once.
init:
	poetry config virtualenvs.in-project true --local
	poetry install

# Development run target. Runs breakpoint statements, asserts and the @timer decorator. 
# Will leverage PDB if there are any breakpoints.
dev:
	poetry run python -X dev agents_playground --log DEBUG

# Run unit tests. Includes all files in ./test named test_*.py and *_test.py.
# To run a single test in a test class do something like:
# 	poetry run pytest ./tests/core/task_scheduler_test.py::TestTaskScheduler::test_running_simple_functions -s
# 
# Use the -s flag to have print statements show up during test runs.
# 	poetry run pytest -k "simulation_test.py" -s
test:
	poetry run pytest

# Step through a test with pudb.
# Place a breakpoint() statement either in the test or in the code under test.
test_debug:
	PYTHONBREAKPOINT="pudb.set_trace" poetry run pytest -k "task_scheduler_test.py" -s

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

# Launch a Nix shell for doing development in.
nix:
	nix-shell --run zsh ./dev/shell.nix
	

# Calculates code coverage.
cov:
	poetry run pytest --cov-report html --cov-report term --cov=agents_playground tests/
	open ./htmlcov/index.html

# Generates the code documentation.
doc:
	poetry run pdoc --html --force --output-dir ./pdocs agents_playground
	open ./pdocs/agents_playground/index.html

# Use line-profiler to profile a function.
# To profile a function, it must be annotated with the @profile decorator.
# The kernprof script adds @profile to the global namespace.
profile_function: 
	poetry run kernprof --line-by-line --view ./agents_playground/__main__.py

# Run cloc to measure the size of the project.
# https://github.com/AlDanial/cloc
# Install cloc with Homebrew.
size:
	@( \
	set -e ; \
	echo "Application Code"; \
	cloc --progress=1 --exclude-dir=__pycache__ ./agents_playground; \
	\
	echo "\nTest Code"; \
	cloc --progress=1 --exclude-dir=__pycache__ ./tests; \
	)

# Run DearPyGUI's demo
demo:
	poetry run python ./demo.py

# Run the Parrallel Spike app.
parrallel:
	poetry run python ./parrallel_spike.py