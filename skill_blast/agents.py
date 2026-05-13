"""
Cross-platform AI agent definitions.
Each agent has: display name, skill directory, detection logic.
"""

import os
import platform
import shutil
from pathlib import Path

HOME = Path.home()
IS_WINDOWS = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"


def _appdata() -> Path:
    """Windows %APPDATA%, macOS ~/Library/Application Support, else HOME."""
    if IS_WINDOWS:
        return Path(os.environ.get("APPDATA", HOME / "AppData" / "Roaming"))
    if IS_MAC:
        return HOME / "Library" / "Application Support"
    return HOME


def _has_cmd(*cmds: str) -> bool:
    return any(shutil.which(c) for c in cmds)


def _dir_exists(*paths: Path) -> bool:
    return any(p.exists() for p in paths)


# ── Agent registry ─────────────────────────────────────────────────────────────
# skills_dir: where skill folders are symlinked/copied for that agent
# detect: returns True if the agent appears to be installed

AGENTS: dict[str, dict] = {
    "claude-code": {
        "name": "Claude Code",
        "icon": "🤖",
        "skills_dir": HOME / ".claude" / "skills",
        "detect": lambda: _dir_exists(HOME / ".claude") or _has_cmd("claude"),
        "docs": "https://docs.anthropic.com/en/docs/claude-code",
        "note": "Load via /skills in Claude Code",
    },
    "opencode": {
        "name": "OpenCode",
        "icon": "⚡",
        "skills_dir": HOME / ".opencode" / "skills",
        "detect": lambda: _dir_exists(HOME / ".opencode") or _has_cmd("opencode"),
        "docs": "https://opencode.ai",
        "note": "Load via /plugin in OpenCode",
    },
    "antigravity": {
        "name": "Antigravity",
        "icon": "🚀",
        "skills_dir": HOME / ".antigravity" / "skills",
        "detect": lambda: _dir_exists(HOME / ".antigravity") or _has_cmd("antigravity"),
        "docs": "https://antigravity.dev",
        "note": "Load via /skills in Antigravity",
    },
    "gemini-cli": {
        "name": "Gemini CLI",
        "icon": "♊",
        "skills_dir": HOME / ".gemini" / "skills",
        "detect": lambda: _dir_exists(HOME / ".gemini") or _has_cmd("gemini", "gemini-cli"),
        "docs": "https://github.com/google-gemini/gemini-cli",
        "note": "Skills auto-loaded from ~/.gemini/skills/",
    },
    "cursor": {
        "name": "Cursor",
        "icon": "🖱️",
        "skills_dir": HOME / ".cursor" / "skills",
        "detect": lambda: _dir_exists(HOME / ".cursor") or _has_cmd("cursor"),
        "docs": "https://cursor.com",
        "note": "Skills available in Cursor agent mode",
    },
    "windsurf": {
        "name": "Windsurf",
        "icon": "🏄",
        "skills_dir": HOME / ".codeium" / "windsurf" / "skills",
        "detect": lambda: _dir_exists(HOME / ".codeium") or _has_cmd("windsurf"),
        "docs": "https://codeium.com/windsurf",
        "note": "Load via Cascade in Windsurf",
    },
    "continue": {
        "name": "Continue.dev",
        "icon": "🔄",
        "skills_dir": HOME / ".continue" / "skills",
        "detect": lambda: _dir_exists(HOME / ".continue") or _has_cmd("continue"),
        "docs": "https://continue.dev",
        "note": "Skills available in Continue sidebar",
    },
    "aider": {
        "name": "Aider",
        "icon": "✏️",
        "skills_dir": HOME / ".aider" / "skills",
        "detect": lambda: _has_cmd("aider"),
        "docs": "https://aider.chat",
        "note": "Reference skill files in your chat",
    },
}


def detect_agents() -> dict[str, dict]:
    """Return agents that appear to be installed on this machine."""
    return {k: v for k, v in AGENTS.items() if v["detect"]()}
