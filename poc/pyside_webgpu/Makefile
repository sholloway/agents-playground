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
	poetry run python -X dev pyside_webgpu --poc playground_wx

# Launch an instance of bpython.
shell:
	poetry run bpython

# Install and run the wxPython Demo. 
# This will download wxPython-demo-4.2.1.tar.gz and run it.
wx_demo:
	poetry run python ../../.venv/lib/python3.11/site-packages/wx/tools/wxget_docs_demo.py "demo"

# Run the ShaderToy clone. 
st: 
	poetry run python pyside_webgpu/shadertoy.py
	
