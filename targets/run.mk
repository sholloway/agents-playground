# PLAYGROUND_LOGGING_LEVEL specifies the granularity to use for logging.
# Options are (in increasing granularity): DEBUG, INFO, WARNING, ERROR, CRITICAL
PLAYGROUND_LOGGING_LEVEL ?= ERROR

# PLAYGROUND_DEBUG_OPTIONS provides a way to specify debug flags  with the various run targets.
#
# By default,  PLAYGROUND_DEBUG_OPTIONS is not set.
# Options are:
# --viz-task-graph: This will trigger the engine to produce visualizations of the task graph during 
# initialization, the first frame rendered, and shutdown. These are written to the 
# current working directory under task_graph_debug_files.
#
# Example:
# PLAYGROUND_DEBUG_OPTIONS=--viz-task-graph make run

# Runs the app in production mode.
# Typical development flow is:
# make check test run
run-default:
	@( \
	source .venv/bin/activate; \
	poetry run python -O agents_playground --log $(PLAYGROUND_LOGGING_LEVEL) $(PLAYGROUND_DEBUG_OPTIONS); \
	)

# Run the app with a sim already selected. 
# TODO: Make this remember the last sim selected and have that be the default. 
# Allow specifying it with a shell variable (e.g. PLAYGROUND_WITH_SIM)
PLAYGROUND_WITH_SIM ?= ~/Documents/my_simulation
run-sim:
	@( \
	source .venv/bin/activate; \
	echo $(PLAYGROUND_LOGGING_LEVEL); \
	poetry run python -O agents_playground --log $(PLAYGROUND_LOGGING_LEVEL) --sim $(PLAYGROUND_WITH_SIM) $(PLAYGROUND_DEBUG_OPTIONS); \
	)

# Development run target. Runs breakpoint statements, asserts and the @timer decorator. 
# Will leverage PDB if there are any breakpoints.
run-dev:
	@( \
	source .venv/bin/activate; \
	poetry run python -X dev agents_playground --log $(PLAYGROUND_LOGGING_LEVEL) $(PLAYGROUND_DEBUG_OPTIONS); \
	)
