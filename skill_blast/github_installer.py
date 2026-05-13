"""
GitHub-hosted skill installer.

Skills are stored in the skill-blast GitHub repository and installed
directly from there via the CLI. This module handles:

1. Fetching skill metadata from the bundled skills.json
2. Pulling skill content directly from the original GitHub repos
3. Parsing sub-agent instructions from SKILL.md / CLAUDE.md / AGENTS.md
4. Installing skills into all supported AI agent CLIs automatically
"""

import json
import re
import subprocess
from pathlib import Path
from typing import Optional

from .skills import Skill, ALL_SKILLS, SKILLS_BY_ID
from .agents import AGENTS, detect_agents
from .registry import register_install, register_uninstall


# ── Constants ──────────────────────────────────────────────────────────────────

SKILL_BLAST_REPO = "Venkatesh-6921/skill-blast"
SKILL_BLAST_RAW_BASE = f"https://raw.githubusercontent.com/{SKILL_BLAST_REPO}/main"

# Files that may contain agent-specific instructions, in priority order.
_INSTRUCTION_FILES = [
    "SKILL.md",
    "skill.md",
    "CLAUDE.md",
    "AGENTS.md",
    "instructions.md",
    "README.md",
]

# Patterns that indicate a skill has sub-agents or multi-agent requirements.
# These are parsed from the instruction files in the original repos.
_SUB_AGENT_PATTERNS = [
    re.compile(r"sub[_-]?agents?\s*:", re.IGNORECASE),
    re.compile(r"requires?\s+(?:sub[_-]?)?agents?", re.IGNORECASE),
    re.compile(r"depends\s+on\s+(?:sub[_-]?)?agents?", re.IGNORECASE),
    re.compile(r"child\s+(?:agents?|skills?)", re.IGNORECASE),
    re.compile(r"bundled\s+skills?", re.IGNORECASE),
    re.compile(r"included?\s+skills?", re.IGNORECASE),
    re.compile(r"(?:also\s+)?install\s+(?:the\s+)?following", re.IGNORECASE),
]

# Patterns for agent-specific install instructions.
_AGENT_INSTALL_PATTERNS = {
    "claude-code": [
        re.compile(r"claude\s*code", re.IGNORECASE),
        re.compile(r"/skills\s+command", re.IGNORECASE),
        re.compile(r"~?/?\.claude/", re.IGNORECASE),
    ],
    "opencode": [
        re.compile(r"opencode", re.IGNORECASE),
        re.compile(r"~?/?\.opencode/", re.IGNORECASE),
    ],
    "antigravity": [
        re.compile(r"antigravity", re.IGNORECASE),
        re.compile(r"~?/?\.antigravity/", re.IGNORECASE),
    ],
    "gemini-cli": [
        re.compile(r"gemini[\s-]?cli", re.IGNORECASE),
        re.compile(r"~?/?\.gemini/", re.IGNORECASE),
    ],
    "cursor": [
        re.compile(r"cursor", re.IGNORECASE),
        re.compile(r"~?/?\.cursor/", re.IGNORECASE),
    ],
    "windsurf": [
        re.compile(r"windsurf", re.IGNORECASE),
        re.compile(r"codeium", re.IGNORECASE),
        re.compile(r"~?/?\.codeium/", re.IGNORECASE),
    ],
    "continue": [
        re.compile(r"continue\.dev", re.IGNORECASE),
        re.compile(r"~?/?\.continue/", re.IGNORECASE),
    ],
    "aider": [
        re.compile(r"aider", re.IGNORECASE),
        re.compile(r"~?/?\.aider/", re.IGNORECASE),
    ],
}


# ── Instruction parsing ───────────────────────────────────────────────────────

def parse_instruction_file(content: str) -> dict:
    """
    Parse a skill's instruction file to extract:
    - supported_agents: list of agent keys the skill explicitly supports
    - has_sub_agents: whether the skill bundles or depends on sub-agents
    - sub_agent_names: list of sub-agent/sub-skill names found
    - install_notes: agent-specific installation notes (dict: agent_key -> text)
    """
    result = {
        "supported_agents": [],
        "has_sub_agents": False,
        "sub_agent_names": [],
        "install_notes": {},
    }

    if not content:
        return result

    # Detect which agents are mentioned in the instruction file
    for agent_key, patterns in _AGENT_INSTALL_PATTERNS.items():
        for pattern in patterns:
            if pattern.search(content):
                if agent_key not in result["supported_agents"]:
                    result["supported_agents"].append(agent_key)
                break

    # Detect sub-agents
    for pattern in _SUB_AGENT_PATTERNS:
        if pattern.search(content):
            result["has_sub_agents"] = True
            break

    # Extract sub-agent names (look for bullet-list style references)
    # Patterns like: - `skill-name` or - skill-name
    sub_agent_re = re.compile(
        r"(?:sub[_-]?agents?|bundled\s+skills?|included?\s+skills?)\s*:.*?"
        r"(?:(?:^|\n)\s*[-*]\s+`?([a-zA-Z0-9_-]+)`?)+",
        re.IGNORECASE | re.DOTALL,
    )
    match = sub_agent_re.search(content)
    if match:
        # Extract all bullet items after the heading
        start = match.start()
        block = content[start:start + 2000]  # limit search scope
        for item_match in re.finditer(r"^\s*[-*]\s+`?([a-zA-Z0-9_-]+)`?", block, re.MULTILINE):
            name = item_match.group(1).strip()
            if name and name not in result["sub_agent_names"]:
                result["sub_agent_names"].append(name)

    return result


def read_instruction_file(skill_dir: Path) -> Optional[str]:
    """
    Read the best available instruction file from a skill directory.
    Returns the file content, or None if no instruction file found.
    """
    for filename in _INSTRUCTION_FILES:
        filepath = skill_dir / filename
        if filepath.exists():
            try:
                return filepath.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
    return None


# ── Multi-agent installation ──────────────────────────────────────────────────

def resolve_target_agents(
    skill: Skill,
    instruction_content: Optional[str] = None,
    explicit_agents: Optional[list[str]] = None,
) -> list[str]:
    """
    Determine which agents a skill should be installed to.

    Priority:
    1. Explicitly specified agents (from CLI --agents flag)
    2. Agents mentioned in the skill's instruction file
    3. All detected agents on the system

    Returns a list of agent keys.
    """
    # User explicitly specified agents — respect their choice
    if explicit_agents:
        return [a for a in explicit_agents if a in AGENTS]

    # Parse instruction file for supported agents
    if instruction_content:
        parsed = parse_instruction_file(instruction_content)
        if parsed["supported_agents"]:
            # Install to supported agents that are detected on this system
            detected = detect_agents()
            resolved = [a for a in parsed["supported_agents"] if a in detected]
            # If none of the supported agents are detected, fall back to all detected
            if resolved:
                return resolved

    # Default: install to all detected agents
    detected = detect_agents()
    return list(detected.keys()) if detected else ["claude-code"]


def resolve_sub_agents(
    skill: Skill,
    instruction_content: Optional[str] = None,
) -> list[Skill]:
    """
    If a skill has sub-agents/sub-skills, resolve them to Skill objects.
    Returns a list of Skill objects that should also be installed.
    """
    if not instruction_content:
        return []

    parsed = parse_instruction_file(instruction_content)
    if not parsed["has_sub_agents"] or not parsed["sub_agent_names"]:
        return []

    sub_skills = []
    for name in parsed["sub_agent_names"]:
        # Look up by name in ALL_SKILLS
        for s in ALL_SKILLS:
            if s.name == name or s.name.replace("-", "_") == name.replace("-", "_"):
                sub_skills.append(s)
                break

    return sub_skills


# ── GitHub-based installation ─────────────────────────────────────────────────

def install_from_github(
    skill: Skill,
    agent_keys: Optional[list[str]] = None,
    dry_run: bool = False,
    update: bool = False,
) -> dict:
    """
    Install a skill from GitHub with full instruction parsing.

    1. Clone/cache the original repo
    2. Parse instruction files for sub-agents and agent support
    3. Install to all resolved target agents
    4. If sub-agents exist, install those too
    5. Register the installation in the local registry

    Returns a result dict with status info.
    """
    from .installer import install_skill, ensure_repo, CACHE_DIR

    result = {
        "skill": skill,
        "ok": False,
        "agents_resolved": [],
        "sub_agents_installed": [],
        "instruction_parsed": False,
        "error": None,
    }

    # Step 1: Ensure the repo is cached
    if not dry_run:
        repo_ok, repo_msg = ensure_repo(skill.repo, update=update)
        if not repo_ok:
            result["error"] = f"GitHub fetch failed: {repo_msg}"
            return result

    # Step 2: Read instruction file from the cached repo
    instruction_content = None
    if not dry_run:
        repo_cache = CACHE_DIR / skill.repo.replace("/", "__")
        skill_dir = repo_cache / skill.subpath if skill.subpath else repo_cache
        instruction_content = read_instruction_file(skill_dir)
        result["instruction_parsed"] = instruction_content is not None

    # Step 3: Resolve which agents to install to
    target_agents = resolve_target_agents(skill, instruction_content, agent_keys)
    result["agents_resolved"] = target_agents
    agent_dirs = [AGENTS[k]["skills_dir"] for k in target_agents if k in AGENTS]

    # Step 4: Install the skill itself
    install_result = install_skill(skill, agent_dirs, dry_run=dry_run, update=update)
    if not install_result["ok"]:
        result["error"] = install_result.get("error", "install failed")
        return result

    # Step 5: Handle sub-agents
    if instruction_content and not dry_run:
        sub_skills = resolve_sub_agents(skill, instruction_content)
        for sub_skill in sub_skills:
            sub_result = install_skill(sub_skill, agent_dirs, dry_run=dry_run, update=update)
            if sub_result["ok"]:
                result["sub_agents_installed"].append(sub_skill.name)
                register_install(sub_skill.name, sub_skill.id, target_agents)

    # Step 6: Register in local registry
    if not dry_run:
        register_install(skill.name, skill.id, target_agents)

    result["ok"] = True
    return result


def uninstall_from_github(
    skill: Skill,
    agent_keys: Optional[list[str]] = None,
) -> dict:
    """
    Uninstall a skill and update the registry.
    """
    from .installer import uninstall_skill

    if agent_keys:
        agent_dirs = [AGENTS[k]["skills_dir"] for k in agent_keys if k in AGENTS]
    else:
        agent_dirs = [a["skills_dir"] for a in AGENTS.values()]

    result = uninstall_skill(skill, agent_dirs)

    if result["ok"]:
        register_uninstall(skill.name)

    return result


def get_install_status() -> dict[str, dict]:
    """
    Get the installation status of all skills.
    Returns { skill_name: { installed: bool, agents: [...], updated_at: str } }
    """
    from .registry import get_installed

    installed = get_installed()
    status = {}

    for skill in ALL_SKILLS:
        entry = installed.get(skill.name)
        status[skill.name] = {
            "installed": entry is not None,
            "agents": entry["agents"] if entry else [],
            "updated_at": entry["updated_at"] if entry else None,
        }

    return status
