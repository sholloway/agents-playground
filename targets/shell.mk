# Launch an instance of bpython.
shell:
	@( \
	source .venv/bin/activate; \
	poetry run bpython; \
	)