# Launches pudb debugger in the terminal if there are any breakpoints. 
run-pudb:
	PYTHONBREAKPOINT="pudb.set_trace" poetry run python -X dev agents_playground --log DEBUG