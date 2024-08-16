VENV = venv
PYTHON = $(VENV)/bin/python
PYTHON_VERSION = 3.11


all: req lint tests


venv:
	python$(PYTHON_VERSION) -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip

req: venv
	$(PYTHON) -m pip install -r requirements.txt


tests: req
	$(PYTHON) -m pytest tests


ruff:
	$(PYTHON) -m ruff .

lint: ruff
