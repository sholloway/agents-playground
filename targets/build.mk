# Builds the project into a distributable wheel.
build-wheel:
	@( \
	source .venv/bin/activate; \
	poetry build;\
	)
