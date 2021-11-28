
################################################################################
# Main Tasks

# Production optimization running target.
run: activate_env
	python -O ./agents_playground/main.py --log ERROR

# Development run target. Runs break statements and asserts. 
dev: activate_env
	python -X dev ./agents_playground/main.py --log DEBUG

# Perform static type checking on the project.
check: activate_env
	mypy --config-file mypy.ini agents_playground

# Launches a debugger in the terminal. 
debug: activate_env
	PYTHONBREAKPOINT="pudb.set_trace" python -X dev ./agents_playground/main.py --log DEBUG

################################################################################
# Supporting Tasks
activate_env: 
	poetry shell
