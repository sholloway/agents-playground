
################################################################################
# Main Tasks

# Production optimization running target.
run: activate_env
	python -O ./agents_playground/main.py --log ERROR

# Development run target. Runs breakpoint statements, asserts and the @timer decorator. 
# Will leverage PDB if there are any breakpoints.
dev: activate_env
	python -X dev ./agents_playground/main.py --log DEBUG

# Perform static type checking on the project.
check: activate_env
	mypy --config-file mypy.ini agents_playground

# Launches pudb debugger in the terminal if there are any breakpoints. 
debug: activate_env
	PYTHONBREAKPOINT="pudb.set_trace" python -X dev ./agents_playground/main.py --log DEBUG
################################################################################
# Supporting Tasks
activate_env: 
	poetry shell
