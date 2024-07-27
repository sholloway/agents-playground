# Creates an isolated Nix shell for working in.
# Note: This is optional. If you're not using Nix and manage your Python install
# some other way, then just ignore this make target.
# Installs Python, git, make, cloc the first time it's run.
env-shell:
	devbox shell

# Create a Python virtual environment, install pip, and install Poetry.
env-setup:
	@( \
	set -e ; \
	python -m venv ./.venv; \
	source .venv/bin/activate; \
	python -m ensurepip --upgrade; \
	python -m pip install --upgrade pip; \
	pip install -r requirements.txt; \
	)

# Initialize the project with Poetry.
# This only needs to be done once.
# There are a few dev dependencies (bpython, line-profiler, pudb)
# that need to be compiled on install. This doesn't play well 
# with the nix-based project setup (i.e. devbox). 
# To work around this:
# 1. make env
# 2. make setup
# 3. exit
# 4. make init
# 5. make env
env-install-dependencies:
	@( \
	source .venv/bin/activate; \
	poetry config virtualenvs.in-project true --local; \
	poetry install; \
	)