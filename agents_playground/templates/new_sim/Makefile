
# Creates an isolated Nix shell for working in.
# Note: This is optional. If you're not using Nix and manage your Python install
# some other way, then just ignore this make target.
# Installs Python, git, make, cloc the first time it's run.
env:
	devbox shell

# Create a Python virtual environment and install Poetry.
# This only needs to be done once.
setup:
	@( \
	set -e ; \
	python -m venv ./.venv; \
	source .venv/bin/activate; \
	python -m ensurepip --upgrade; \
	python -m pip install --upgrade pip; \
	pip install -r requirements.txt; \
	)

# Initialize the project with Poetry.
# This only needs to be done once.
init:
	@( \
	source .venv/bin/activate; \
	poetry config virtualenvs.in-project true --local; \
	poetry install; \
	)

# Run unit tests. Includes all files in ./tests named test_*.py and *_test.py.
# To run a single test in a test class do something like:
# 	poetry run pytest ./tests/core/task_scheduler_test.py::TestTaskScheduler::test_running_simple_functions -s
# 
# Use the -s flag to have print statements show up during test runs.
# 	poetry run pytest -k "simulation_test.py" -s
test:
	@( \
	poetry run pytest; \
	)