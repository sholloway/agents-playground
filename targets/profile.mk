# Launch's py-spy profiler and generates an interactive flame graph.
# It then opens Speedcope in the browser. 
flame:
	sudo poetry run py-spy record \
		--output profile.speedscope.json \
		--threads \
		--rate 1000 \
		--format speedscope -- python -X dev agents_playground --log DEBUG
	
	speedscope ./profile.speedscope.json

# Display a running list of the top most expensive functions while the app is running.
top:
	@( \
	source .venv/bin/activate; \
	sudo poetry run py-spy top -- python agents_playground; \
	)

# Use line-profiler to profile a function.
# To profile a function, it must be annotated with the @profile decorator.
# The kernprof script adds @profile to the global namespace.
#
# You can view the generated lprof file like this.
# poetry run python -m line_profiler pytest.lprof
#
# On my computer the time unit is 1e-06 s which is 1 millionth of a second.
# That is a microsecond (µs)
profile-function: 
	poetry run kernprof --line-by-line --view ./agents_playground/__main__.py

# Profile a specific unit test.
profile-test:
	@( \
	source .venv/bin/activate; \
	poetry run kernprof --line-by-line --view pytest  ./tests/spatial/coordinate_test.py::TestProfilingCoordinates::test_profile; \
	) \