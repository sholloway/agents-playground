# Run unit tests. Includes all files in ./test named test_*.py and *_test.py.
# To run a single test in a test class do something like:
# 	poetry run pytest ./tests/core/task_scheduler_test.py::TestTaskScheduler::test_running_simple_functions -s
# 
# Use the -s flag to have print statements show up during test runs.
# 	poetry run pytest -k "simulation_test.py" -s
#
# Use --durations=0 to find slow running tests.
# 	poetry run pytest --durations=0
test:
	@( \
	poetry run pytest; \
	)

# Step through a test with pudb.
# Place a breakpoint() statement either in the test or in the code under test.
test_debug:
	PYTHONBREAKPOINT="pudb.set_trace" poetry run pytest -k "task_scheduler_test.py" -s

# Calculates code coverage.
cov:
	poetry run pytest --cov-report html --cov-report term --cov=agents_playground tests/
	open ./htmlcov/index.html