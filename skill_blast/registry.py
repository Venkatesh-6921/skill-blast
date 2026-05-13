"""
Local skill registry — tracks installed skills, timestamps, and target agents.

File: ~/.skill-blast/registry.json
Schema: { "<skill_name>": { "skill_id": int, "installed_at": str, "updated_at": str, "agents": [...], "version": str } }
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

HOME = Path.home()
REGISTRY_FILE = HOME / ".skill-blast" / "registry.json"


def _load() -> dict:
    """Load the registry from disk. Returns empty dict if missing/corrupt."""
    if not REGISTRY_FILE.exists():
        return {}
    try:
        return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save(data: dict) -> None:
    """Persist the registry to disk using atomic write (temp file + os.replace)."""
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = REGISTRY_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(tmp, REGISTRY_FILE)  # atomic on POSIX and Windows


def register_install(skill_name: str, skill_id: int, agents: list[str], version: str = "latest") -> None:
    """Record a skill installation in the registry."""
    data = _load()
    now = datetime.now(timezone.utc).isoformat()
    data[skill_name] = {
        "skill_id": skill_id,
        "installed_at": data.get(skill_name, {}).get("installed_at", now),
        "updated_at": now,
        "agents": sorted(set(agents)),
        "version": version,
    }
    _save(data)


def register_uninstall(skill_name: str) -> None:
    """Remove a skill from the registry."""
    data = _load()
    data.pop(skill_name, None)
    _save(data)


def is_installed(skill_name: str) -> bool:
    """Check if a skill is tracked as installed."""
    return skill_name in _load()


def get_installed() -> dict:
    """Return all installed skill entries."""
    return _load()


def get_entry(skill_name: str) -> Optional[dict]:
    """Return a single skill's registry entry, or None."""
    return _load().get(skill_name)


def clear_registry() -> None:
    """Wipe the registry (used in tests or hard reset)."""
    if REGISTRY_FILE.exists():
        REGISTRY_FILE.unlink()
