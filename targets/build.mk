# Builds the project into a distributable wheel.
build:
	@( \
	source .venv/bin/activate; \
	poetry build;\
	)
