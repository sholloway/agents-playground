SHELL = /bin/sh

run: 
	poetry run main

activate_env: 
	poetry shell

check: activate_env
	mypy agents_playground