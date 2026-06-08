# =============================================================================
#  DMML Makefile — Developer convenience targets
#  Usage:  make          → same as `make start`
#          make start    → launch with Ollama (offline)
#          make openai   → launch with OpenAI
#          make debug    → launch in debug mode (enables /debug/* routes)
#          make install  → install dependencies only
#          make migrate  → run pending migrations
#          make shortcut → install desktop shortcut (Linux)
#          make clean    → remove .venv and __pycache__
# =============================================================================

SHELL      := /bin/bash
PYTHON     := .venv/bin/python3
PIP        := .venv/bin/pip
FLASK      := .venv/bin/flask
PORT       ?= 5000

.PHONY: all start openai debug install migrate shortcut clean help

all: start

## Launch the app with Ollama (no API key required)
start: install migrate
	@AI_PROVIDER=ollama PORT=$(PORT) $(PYTHON) run.py

## Launch the app with OpenAI (requires OPENAI_API_KEY in .env)
openai: install migrate
	@AI_PROVIDER=openai PORT=$(PORT) $(PYTHON) run.py

## Launch in debug mode (enables /debug/* routes + auto-reload)
debug: install migrate
	@AI_PROVIDER=ollama FLASK_DEBUG=1 PORT=$(PORT) $(PYTHON) run.py

## Install / update Python dependencies
install: .venv/bin/python3
	@echo "▶ Installing dependencies..."
	@$(PIP) install -r requirements.txt -q --disable-pip-version-check
	@echo "✔ Dependencies up to date"

## Create the virtual environment if it doesn't exist
.venv/bin/python3:
	@echo "▶ Creating virtual environment..."
	@python3 -m venv .venv
	@echo "✔ .venv created"

## Apply pending Alembic migrations
migrate: .venv/bin/python3
	@FLASK_APP=run.py $(FLASK) db upgrade --quiet 2>/dev/null || FLASK_APP=run.py $(FLASK) db upgrade
	@echo "✔ Database up to date"

## Install the Linux desktop shortcut
shortcut:
	@bash install_shortcut.sh

## Remove the virtual environment and Python bytecode caches
clean:
	@echo "▶ Cleaning..."
	@rm -rf .venv
	@find . -type d -name "__pycache__" -not -path "./.git/*" -exec rm -rf {} + 2>/dev/null || true
	@echo "✔ Clean complete"

## Show this help message
help:
	@echo ""
	@echo "  DMML — Available targets:"
	@grep -E '^## ' Makefile | sed 's/## /    /'
	@echo ""
