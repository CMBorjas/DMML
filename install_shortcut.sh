#!/usr/bin/env bash
# =============================================================================
#  DMML — Linux Desktop Shortcut Installer
#  Creates an app-menu entry and an optional Desktop shortcut.
#  Usage: ./install_shortcut.sh
# =============================================================================

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ICON="$PROJECT_DIR/app/static/icon.png"
START_SCRIPT="$PROJECT_DIR/start.sh"
APPS_DIR="$HOME/.local/share/applications"
DESKTOP_DIR="$HOME/Desktop"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✔ $1${NC}"; }
step() { echo -e "${YELLOW}▶ $1${NC}"; }

# Ensure start.sh is executable
chmod +x "$START_SCRIPT"

DESKTOP_CONTENT="[Desktop Entry]
Version=1.0
Type=Application
Name=Dungeon Master Assistant
GenericName=DMML
Comment=AI-powered D&D 5e campaign assistant
Exec=bash -c 'cd \"$PROJECT_DIR\" && ./start.sh'
Icon=$ICON
Terminal=true
Categories=Game;RolePlay;Education;
Keywords=DnD;DungeonMaster;RPG;AI;
StartupNotify=true
"

# ── App menu entry ────────────────────────────────────────────────────────────
step "Installing app menu entry..."
mkdir -p "$APPS_DIR"
echo "$DESKTOP_CONTENT" > "$APPS_DIR/dmml.desktop"
chmod +x "$APPS_DIR/dmml.desktop"
ok "App menu entry: $APPS_DIR/dmml.desktop"

# Update desktop database if the tool is available
if command -v update-desktop-database &>/dev/null; then
    update-desktop-database "$APPS_DIR" 2>/dev/null || true
fi

# ── Desktop shortcut ─────────────────────────────────────────────────────────
if [ -d "$DESKTOP_DIR" ]; then
    step "Installing Desktop shortcut..."
    echo "$DESKTOP_CONTENT" > "$DESKTOP_DIR/dmml.desktop"
    chmod +x "$DESKTOP_DIR/dmml.desktop"
    # Trust the shortcut on GNOME / KDE desktops
    if command -v gio &>/dev/null; then
        gio set "$DESKTOP_DIR/dmml.desktop" metadata::trusted true 2>/dev/null || true
    fi
    ok "Desktop shortcut: $DESKTOP_DIR/dmml.desktop"
else
    echo -e "${YELLOW}⚠ No ~/Desktop folder found — skipping desktop shortcut.${NC}"
    echo -e "  To create it manually, copy: $APPS_DIR/dmml.desktop → your Desktop."
fi

echo ""
ok "Done! Look for 'Dungeon Master Assistant' in your app launcher,"
ok "or double-click the icon on your Desktop."
