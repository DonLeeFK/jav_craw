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

clean:
	rm -rf $(VENV_DIR)

.PHONY: install run clean
