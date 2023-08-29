# Launch a Nix shell for doing development in.
# Note: This is optional. If you're not using Nix and manage your Python install
# some other way, then just ignore this make target.
nix:
	nix-shell --run zsh ../dev/shell.nix

# Initialize the project with Poetry.
# This only needs to be done once.
init:
	poetry config virtualenvs.in-project true --local
	poetry install

# Runs the app in production mode.
run:
	poetry run python -O pyside_webgpu --poc wx_triangle

# Development run target. Runs breakpoint statements and asserts. 
# Will leverage PDB if there are any breakpoints.
dev:
	poetry run python -X dev 	poetry run python -O pyside_webgpu