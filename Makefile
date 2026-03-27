PYTHON ?= python3
VENV ?= .venv
PIP := $(VENV)/bin/pip
PYTHON_VENV := $(VENV)/bin/python

.PHONY: setup-backend install-backend test-backend run-backend frontend-install frontend-dev

setup-backend:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip

install-backend: setup-backend
	$(PIP) install -r backend/requirements.txt

test-backend:
	$(PYTHON) -m unittest tests.test_backend_core -v

run-backend:
	$(PYTHON) -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000

frontend-install:
	npm install

frontend-dev:
	npm run dev
