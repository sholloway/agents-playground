# Run DearPyGUI's demo
demo:
	poetry run python ./demo.py

# Run the Parrallel Spike app.
parrallel:
	poetry run python ./parrallel_spike.py


# Install and run the wxPython Demo. 
# This will download wxPython-demo-4.2.1.tar.gz and run it.
wx_demo:
	poetry run python .venv/lib/python3.11/site-packages/wx/tools/wxget_docs_demo.py "demo"


