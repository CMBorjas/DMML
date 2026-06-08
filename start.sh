#!/usr/bin/env bash
# =============================================================================
#  DMML Launcher — Linux / macOS
#  Run this once to set everything up and start the server.
#  Usage:  ./start.sh
#          ./start.sh --provider ollama
#          ./start.sh --provider openai --debug
# =============================================================================

set -euo pipefail

# ── Resolve project root regardless of where script is called from ───────────
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
PYTHON="$VENV_DIR/bin/python3"
PIP="$VENV_DIR/bin/pip"
FLASK="$VENV_DIR/bin/flask"

# ── Defaults (overridable via flags) ─────────────────────────────────────────
AI_PROVIDER="${AI_PROVIDER:-ollama}"
FLASK_DEBUG="${FLASK_DEBUG:-0}"
PORT="${PORT:-5000}"

# ── Parse CLI flags ───────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --provider|-p) AI_PROVIDER="$2"; shift 2 ;;
        --debug|-d)    FLASK_DEBUG=1;    shift   ;;
        --port)        PORT="$2";        shift 2 ;;
        --help|-h)
            echo "Usage: ./start.sh [--provider openai|ollama] [--debug] [--port 5000]"
            exit 0 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# ── Pretty print helpers ──────────────────────────────────────────────────────
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

banner() {
    echo -e ""
    echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}${BOLD}║   Dungeon Master Machine Language  v1.0  ║${NC}"
    echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════╝${NC}"
    echo -e "${CYAN}  AI Provider : ${BOLD}$AI_PROVIDER${NC}"
    echo -e "${CYAN}  Address     : ${BOLD}http://127.0.0.1:$PORT${NC}"
    echo -e "${CYAN}  Debug mode  : ${BOLD}$([ "$FLASK_DEBUG" = "1" ] && echo ON || echo OFF)${NC}"
    echo -e ""
}

step() { echo -e "${YELLOW}▶ $1${NC}"; }
ok()   { echo -e "${GREEN}✔ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠ $1${NC}"; }
fail() { echo -e "${RED}✖ $1${NC}"; exit 1; }

banner

# ── 1. Check Python ───────────────────────────────────────────────────────────
step "Checking Python 3..."
if ! command -v python3 &>/dev/null; then
    fail "python3 not found. Install Python 3.10+ and try again."
fi
PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
ok "Found Python $PY_VER"

# ── 2. Create venv if missing ─────────────────────────────────────────────────
if [ ! -f "$PYTHON" ]; then
    step "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    ok "Virtual environment created at .venv/"
else
    ok "Virtual environment exists"
fi

# ── 3. Install / upgrade dependencies ────────────────────────────────────────
step "Checking dependencies..."
$PIP install -r "$PROJECT_DIR/requirements.txt" -q --disable-pip-version-check 2>&1 \
    | grep -E "^(Successfully|ERROR|error)" || true
ok "Dependencies up to date"

# ── 4. Bootstrap .env if missing ─────────────────────────────────────────────
if [ ! -f "$PROJECT_DIR/.env" ]; then
    step "No .env found — copying from .env.example..."
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    warn "Edit .env to set your API keys before using OpenAI features."
else
    ok ".env file found"
fi

# Override provider in environment for this session
export AI_PROVIDER
export FLASK_DEBUG
export PORT

# ── 5. Apply database migrations ─────────────────────────────────────────────
step "Applying database migrations..."
cd "$PROJECT_DIR"
FLASK_APP=run.py $FLASK db upgrade --quiet 2>/dev/null || FLASK_APP=run.py $FLASK db upgrade
ok "Database is up to date"

# ── 6. Open browser after the server starts ───────────────────────────────────
open_browser() {
    sleep 3
    if command -v xdg-open &>/dev/null; then
        xdg-open "http://127.0.0.1:$PORT" &>/dev/null &
    elif command -v open &>/dev/null; then   # macOS
        open "http://127.0.0.1:$PORT" &
    fi
}
open_browser &

# ── 7. Launch Flask ───────────────────────────────────────────────────────────
echo -e ""
echo -e "${GREEN}${BOLD}Starting server... (press Ctrl+C to stop)${NC}"
echo -e ""
exec "$PYTHON" "$PROJECT_DIR/run.py"
