# Generates the code documentation.
doc:
	poetry run pdoc --html --force --output-dir ./pdocs agents_playground
	open ./pdocs/agents_playground/index.html
