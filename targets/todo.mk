# Find TODO comments in the codebase.
find-todos:
	@grep \
		--exclude-dir={.benchmarks,.devbox,.mypy_cache,.pytest_cache,.venv,.vscode} \
		--exclude-dir={dist,htmlcov,targets,wgpu_traces} \
		--exclude=Makefile \
		--text \
		--color \
		--line-number \
		-R \
		--only-matching \
		--extended-regexp \
		' TODO:.*|SkipNow' .