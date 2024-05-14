.PHONY: env setup init run run_sim run_classic dev test test_debug benchmark viz_benchmark check debug flame top shell cov doc profile_function profile_test size demo parrallel build wx_demo scan

# Creates an isolated Nix shell for working in.
# Note: This is optional. If you're not using Nix and manage your Python install
# some other way, then just ignore this make target.
# Installs Python, git, make, cloc the first time it's run.
env:
	devbox shell

# Create a Python virtual environment, install pip, and install Poetry.
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
# There are a few dev dependencies (bpython, line-profiler, pudb)
# that need to be compiled on install. This doesn't play well 
# with the nix-based project setup (i.e. devbox). 
# To work around this:
# 1. make env
# 2. make setup
# 3. exit
# 4. make init
# 5. make env
init:
	@( \
	source .venv/bin/activate; \
	poetry config virtualenvs.in-project true --local; \
	poetry install; \
	)

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

# Run all of the benchmark tests.
# 
# Outputs a table with the following columns:
# 	min: The fastest round.
# 	mean: The average round
# 	max: The slowest round
#		median: The 50th-percentile.
#		stddev: The standard deviation. Lower values suggest more consistent performance.
#		iqr: (Interquartile Range): A statistical measure that represents the range 
#         between the first quartile (25th percentile) and the third quartile 
#         (75th percentile) of a dataset. A larger IQR could indicate more 
#					variability in performance, while a smaller IQR suggests more consistent performance.
#		outliers: Data points that significantly deviate from the rest of the data in a dataset.
#		ops: 1000 operations per second. Higher the better.
#		rounds: The number of times a benchmark round was ran.
#		iterations: The number of iterations per round.
benchmark:
	@( \
	source .venv/bin/activate; \
	poetry run pytest ./benchmarks --benchmark-columns="min, mean, max, median, stddev, iqr, outliers, ops, rounds, iterations"; \
	)

# Run the benchmarks and generate histograms for each test group.
# Use the -m option to only generate an image for a specific group name.
viz_benchmark:
	poetry run pytest ./benchmarks --benchmark-histogram=./benchmark_histograms/$(shell date +%m_%d_%y@%H_%M)/

# Perform static type checking on the project.
check:
	poetry run mypy --check-untyped-defs --config-file mypy.ini agents_playground

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
	@( \
	source .venv/bin/activate; \
	sudo poetry run py-spy top -- python agents_playground; \
	)

# Launch an instance of bpython.
shell:
	@( \
	source .venv/bin/activate; \
	poetry run bpython; \
	)

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
#
# You can view the generated lprof file like this.
# poetry run python -m line_profiler pytest.lprof
#
# On my computer the time unit is 1e-06 s which is 1 millionth of a second.
# That is a microsecond (µs)
profile_function: 
	poetry run kernprof --line-by-line --view ./agents_playground/__main__.py

profile_test:
	@( \
	source .venv/bin/activate; \
	poetry run kernprof --line-by-line --view pytest  ./tests/spatial/mesh_test.py::TestHalfEdgeMesh::test_load_skull; \
	) \

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

# Run DearPyGUI's demo
demo:
	poetry run python ./demo.py

# Run the Parrallel Spike app.
parrallel:
	poetry run python ./parrallel_spike.py

# Builds the project into a distributable wheel.
build:
	@( \
	source .venv/bin/activate; \
	poetry build;\
	)

# Install and run the wxPython Demo. 
# This will download wxPython-demo-4.2.1.tar.gz and run it.
wx_demo:
	poetry run python .venv/lib/python3.11/site-packages/wx/tools/wxget_docs_demo.py "demo"

# Scan the codebase for antipatterns.
scan:
	@( \
	source .venv/bin/activate; \
	poetry run flake8 agents_playground/; \
	)