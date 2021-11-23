
run: 
	poetry run main

activate_env: 
	poetry shell

check: activate_env
	mypy --config-file mypy.ini agents_playground