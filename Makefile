VENV_DIR = .venv
REQUIREMENTS_FILE = requirements.txt
PYTHON_SCRIPT = main.py
PYTHON = $(VENV_DIR)/bin/python

$(VENV_DIR):
	python3 -m venv $(VENV_DIR)

install: $(VENV_DIR)
	$(VENV_DIR)/bin/pip install -r $(REQUIREMENTS_FILE)

run: install
	$(PYTHON) $(PYTHON_SCRIPT) $(ARGS)

magnet: install
	$(PYTHON) magnet.py

analyze: install
	$(PYTHON) data.py
clean:
	rm -rf $(VENV_DIR)
	rm -rf __pycache__

.PHONY: install run clean
