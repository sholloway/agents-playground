# Launch an instance of bpython.
run-shell:
	@( \
	source .venv/bin/activate; \
	poetry run bpython; \
	)