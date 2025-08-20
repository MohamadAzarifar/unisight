# Install and Run

- install python 3.12.7
- clone project
- create a new virtual environment using vscode command pallet.
- activate environment bu using 'source .venv/bin/activate'
- on "ModuleNotFoundError: No module named X", run 'pip install X'
- if any package is installed manually, run 'pip freeze > requirements.txt' command to add the name to requirements file.
- run app using 'python -m streamlit run src/app.py'