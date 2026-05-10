#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════╗
# ║  skill-blast — Linux / macOS installer                      ║
# ║  One-liner:  curl -fsSL https://raw.githubusercontent.com/  ║
# ║    Venkatesh-6921/skill-blast/main/install.sh | bash         ║
# ╚══════════════════════════════════════════════════════════════╝

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${CYAN}▶${RESET}  $*"; }
success() { echo -e "${GREEN}✓${RESET}  $*"; }
warn()    { echo -e "${YELLOW}⚠${RESET}  $*"; }
error()   { echo -e "${RED}✗${RESET}  $*" >&2; }
die()     { error "$*"; exit 1; }

echo ""
echo -e "${BOLD}${CYAN}  skill-blast — 50 AI Agent Skills Installer${RESET}"
echo -e "${CYAN}  ─────────────────────────────────────────────${RESET}"
echo ""

# ── Python check ───────────────────────────────────────────────────────────────
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        VER=$("$cmd" -c "import sys; print(sys.version_info.minor)" 2>/dev/null || echo "0")
        MAJOR=$("$cmd" -c "import sys; print(sys.version_info.major)" 2>/dev/null || echo "0")
        if [[ "$MAJOR" -ge 3 && "$VER" -ge 9 ]]; then
            PYTHON="$cmd"
            break
        fi
    fi
done

if [[ -z "$PYTHON" ]]; then
    error "Python 3.9+ not found."
    echo ""
    echo "  Install Python:"
    echo "    macOS:  brew install python   OR  https://python.org/downloads"
    echo "    Ubuntu: sudo apt install python3"
    echo "    Fedora: sudo dnf install python3"
    echo ""
    die "Please install Python 3.9+ and re-run this script."
fi
success "Python found: $($PYTHON --version)"

# ── git check ──────────────────────────────────────────────────────────────────
if ! command -v git &>/dev/null; then
    error "git not found."
    echo ""
    echo "  Install git:"
    echo "    macOS:  brew install git   OR  xcode-select --install"
    echo "    Ubuntu: sudo apt install git"
    echo "    Fedora: sudo dnf install git"
    echo ""
    die "Please install git and re-run this script."
fi
success "git found: $(git --version)"

# ── pip install skill-blast ────────────────────────────────────────────────────
info "Installing skill-blast via pip…"

# Try pip install; handle externally-managed environments (Fedora/Ubuntu 23+)
if ! "$PYTHON" -m pip install --quiet --upgrade skill-blast 2>/dev/null; then
    warn "System pip blocked. Trying --break-system-packages…"
    if ! "$PYTHON" -m pip install --quiet --upgrade skill-blast --break-system-packages 2>/dev/null; then
        warn "Trying user install…"
        "$PYTHON" -m pip install --quiet --upgrade skill-blast --user \
            || die "pip install failed. Try: pipx install skill-blast"
    fi
fi

success "skill-blast installed!"

# ── Verify ─────────────────────────────────────────────────────────────────────
# Try to find the skill-blast binary
SB_CMD=""
for candidate in skill-blast "$HOME/.local/bin/skill-blast"; do
    if command -v skill-blast &>/dev/null; then
        SB_CMD="skill-blast"
        break
    fi
    if [[ -x "$candidate" ]]; then
        SB_CMD="$candidate"
        break
    fi
done

if [[ -z "$SB_CMD" ]]; then
    # Fall back to python -m
    SB_CMD="$PYTHON -m skill_blast"
    warn "skill-blast binary not in PATH. Using: $SB_CMD"
    echo "  Add ~/.local/bin to PATH if needed:"
    echo "    echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc && source ~/.bashrc"
    echo ""
fi

echo ""
echo -e "${BOLD}${GREEN}  ✓ Ready! Launching skill-blast…${RESET}"
echo ""
sleep 1

# ── Run ────────────────────────────────────────────────────────────────────────
exec $SB_CMD "$@"
