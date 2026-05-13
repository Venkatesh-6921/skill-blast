"""
Core installation logic.
- Clone/update GitHub repos to cache
- Copy skill directories to central store
- Symlink (or copy on Windows) into each agent's skills directory
"""

import os
import platform
import shutil
import subprocess
import threading
from collections import defaultdict
from pathlib import Path
from typing import Optional

from .skills import Skill
from .registry import register_install, register_uninstall

HOME = Path.home()
IS_WINDOWS = platform.system() == "Windows"

CACHE_DIR = HOME / ".skill-blast" / "cache"
STORE_DIR = HOME / ".skill-blast" / "skills"

FAILED_REPOS: set[str] = set()   # repos that failed this session — skip retries
_FAILED_LOCK = threading.Lock()  # protects FAILED_REPOS in concurrent installs
UPDATED_REPOS: set[str] = set()
_REPO_LOCKS = defaultdict(threading.Lock)


# ── Git helpers ────────────────────────────────────────────────────────────────

def _run(cmd: list[str], cwd: Optional[Path] = None) -> tuple[bool, str]:
    """Run a command, return (success, last_line_of_stderr_or_stdout)."""
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=120)
        if r.returncode == 0:
            out = (r.stdout or "").strip().splitlines()
            return True, out[-1] if out else "ok"
        err = (r.stderr or "").strip().splitlines()
        return False, err[-1] if err else "unknown error"
    except FileNotFoundError:
        return False, "git not found — please install git (https://git-scm.com)"
    except subprocess.TimeoutExpired:
        return False, "git timed out after 120s"


def check_git() -> tuple[bool, str]:
    return _run(["git", "--version"])


def _clone(repo: str, dest: Path) -> tuple[bool, str]:
    url = f"https://github.com/{repo}.git"
    return _run(["git", "clone", "--depth=1", "--quiet", url, str(dest)])


def _pull(dest: Path) -> tuple[bool, str]:
    _run(["git", "fetch", "--depth=1", "origin", "HEAD", "--quiet"], cwd=dest)
    return _run(["git", "reset", "--hard", "FETCH_HEAD", "--quiet"], cwd=dest)


def ensure_repo(repo: str, update: bool = False) -> tuple[bool, str]:
    """Clone repo if missing; optionally pull if it exists. Returns (ok, message)."""
    with _FAILED_LOCK:
        if repo in FAILED_REPOS:
            return False, "skipped (failed earlier)"

    dest = CACHE_DIR / repo.replace("/", "__")

    with _REPO_LOCKS[repo]:
        if dest.exists():
            if update and repo not in UPDATED_REPOS:
                ok, msg = _pull(dest)
                if not ok:
                    with _FAILED_LOCK:
                        FAILED_REPOS.add(repo)
                else:
                    UPDATED_REPOS.add(repo)
                return ok, f"updated — {msg}"
            return True, "cached" if not update else "updated — ok"

        dest.parent.mkdir(parents=True, exist_ok=True)
        ok, msg = _clone(repo, dest)
        if not ok:
            with _FAILED_LOCK:
                FAILED_REPOS.add(repo)
        else:
            UPDATED_REPOS.add(repo)
        return ok, msg


def batch_update_repos(repos: list[str], max_workers: int = 4) -> dict[str, tuple[bool, str]]:
    """
    Concurrently update multiple cached repos using a thread pool.
    Returns {repo: (ok, message)} for each repo.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    results: dict[str, tuple[bool, str]] = {}

    def _update_one(repo: str) -> tuple[str, bool, str]:
        ok, msg = ensure_repo(repo, update=True)
        return repo, ok, msg

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_update_one, r): r for r in repos}
        for future in as_completed(futures):
            repo, ok, msg = future.result()
            results[repo] = (ok, msg)

    return results


# ── Skill installation ─────────────────────────────────────────────────────────

# Candidate files to use as SKILL.md content, in priority order.
_SKILL_CANDIDATES = [
    "skill.md",        # lowercase variant (e.g. daydream)
    "CLAUDE.md",       # many repos use this for Claude instructions
    "AGENTS.md",       # multi-agent instruction files
    "instructions.md", # generic instruction files
    "README.md",       # fallback: repo readme
]


def _ensure_skill_md(skill_dir: Path, skill: Skill) -> None:
    """
    If the skill directory lacks a SKILL.md, create one from the best
    available candidate file so that Claude Code's /skills can discover it.
    The original file is preserved; SKILL.md is a copy of its content.
    """
    skill_md = skill_dir / "SKILL.md"
    
    if not skill_md.exists():
        for candidate in _SKILL_CANDIDATES:
            source = skill_dir / candidate
            if source.exists():
                try:
                    skill_md.write_text(source.read_text(encoding="utf-8", errors="replace"))
                except Exception:
                    pass  # non-critical — skill still works, just won't appear in /skills
                break

    _ensure_frontmatter(skill_md, skill)

def _ensure_frontmatter(skill_md: Path, skill: Skill) -> None:
    """
    Claude Code ONLY recognizes SKILL.md files that begin with YAML frontmatter.
    If the file exists but lacks frontmatter, we inject it using our metadata.
    """
    if not skill_md.exists():
        return
        
    try:
        content = skill_md.read_text(encoding="utf-8", errors="replace")
        if not content.strip().startswith("---"):
            frontmatter = f"---\nname: {skill.name}\ndescription: {skill.desc}\n---\n\n"
            skill_md.write_text(frontmatter + content, encoding="utf-8")
    except Exception:
        pass


def _link_or_copy(src: Path, dest: Path) -> None:
    """Symlink on Linux/macOS; directory copy on Windows (no symlink privileges by default)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() or dest.is_symlink():
        return
    if IS_WINDOWS:
        shutil.copytree(src, dest)
    else:
        dest.symlink_to(src.resolve())


def install_skill(
    skill: Skill,
    agent_dirs: list[Path],
    dry_run: bool = False,
    update: bool = False,
) -> dict:
    """
    1. Ensure repo is in cache
    2. Resolve source directory (subpath or full repo)
    3. Copy to central store (~/.skill-blast/skills/<name>/)
    4. Ensure SKILL.md exists (auto-generate from best candidate)
    5. Symlink/copy from each agent's skills dir
    Returns a result dict.
    """
    result: dict = {
        "skill": skill,
        "ok": False,
        "repo_msg": "",
        "linked": [],
        "already": [],
        "error": None,
    }

    # ── 1. Repo ────────────────────────────────────────────────────────────────
    if not dry_run:
        repo_ok, repo_msg = ensure_repo(skill.repo, update=update)
        result["repo_msg"] = repo_msg
        if not repo_ok:
            result["error"] = repo_msg
            return result
    else:
        result["repo_msg"] = "dry-run"

    # ── 2. Resolve source ──────────────────────────────────────────────────────
    repo_cache = CACHE_DIR / skill.repo.replace("/", "__")
    if skill.subpath:
        src = repo_cache / skill.subpath
        if not dry_run and not src.exists():
            # subpath may differ; fall back to repo root
            src = repo_cache
    else:
        src = repo_cache

    # ── 3. Central store ───────────────────────────────────────────────────────
    store_dest = STORE_DIR / skill.name
    if not dry_run:
        STORE_DIR.mkdir(parents=True, exist_ok=True)
        if update and store_dest.exists():
            skill_md = store_dest / "SKILL.md"
            if skill_md.exists():
                import shutil as _shutil
                _shutil.copy2(skill_md, store_dest / "SKILL.md.bak")
            try:
                shutil.copytree(src, store_dest, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git"))
            except Exception as e:
                result["error"] = f"update failed: {e}"
                return result
        elif not store_dest.exists():
            try:
                shutil.copytree(src, store_dest, ignore=shutil.ignore_patterns(".git"))
            except Exception as e:
                result["error"] = f"copy failed: {e}"
                return result

    # ── 4. Ensure SKILL.md exists ──────────────────────────────────────────────
    if not dry_run:
        _ensure_skill_md(store_dest, skill)

    # ── 5. Agent links ─────────────────────────────────────────────────────────
    for agent_dir in agent_dirs:
        link = agent_dir / skill.name
        if not dry_run:
            if link.exists() or link.is_symlink():
                result["already"].append(agent_dir.parent.parent.name)
                continue
            try:
                _link_or_copy(store_dest, link)
                result["linked"].append(agent_dir.parent.parent.name)
            except Exception as e:
                result["already"].append(f"err({e})")
        else:
            result["linked"].append(agent_dir.parent.parent.name + "(dry)")


    result["ok"] = True

    # Track in local registry
    if not dry_run and result["ok"]:
        agent_names = [d.parent.parent.name for d in agent_dirs]
        register_install(skill.name, skill.id, agent_names)

    return result


# ── Uninstall ──────────────────────────────────────────────────────────────────

def uninstall_skill(skill: Skill, agent_dirs: list[Path]) -> dict:
    """
    Remove a skill's symlinks/copies from each agent directory
    and optionally remove it from the central store.
    Returns a result dict.
    """
    result: dict = {
        "skill": skill,
        "ok": False,
        "removed": [],
        "not_found": [],
        "error": None,
    }

    # Remove from each agent directory
    for agent_dir in agent_dirs:
        link = agent_dir / skill.name
        if link.exists() or link.is_symlink():
            try:
                if link.is_symlink() or link.is_file():
                    link.unlink()
                elif link.is_dir():
                    shutil.rmtree(link)
                result["removed"].append(agent_dir.parent.parent.name)
            except Exception as e:
                result["error"] = f"remove failed: {e}"
                return result
        else:
            result["not_found"].append(agent_dir.parent.parent.name)

    # Remove from central store
    store_dest = STORE_DIR / skill.name
    if store_dest.exists():
        try:
            shutil.rmtree(store_dest)
        except Exception as e:
            result["error"] = f"store cleanup failed: {e}"
            return result

    result["ok"] = True

    # Remove from registry
    if result["ok"]:
        register_uninstall(skill.name)

    return result


# ── Health check ───────────────────────────────────────────────────────────────

def health_check(agent_dirs: list[Path]) -> dict:
    """
    Check the health of the skill-blast installation.
    Returns a dict with cache_ok, store_ok, broken_links, git_ok.
    """
    report: dict = {
        "git_ok": False,
        "git_msg": "",
        "cache_exists": CACHE_DIR.exists(),
        "store_exists": STORE_DIR.exists(),
        "cached_repos": 0,
        "stored_skills": 0,
        "broken_links": [],
        "healthy_links": 0,
    }

    # Git check
    git_ok, git_msg = check_git()
    report["git_ok"] = git_ok
    report["git_msg"] = git_msg

    # Count cached repos
    if CACHE_DIR.exists():
        report["cached_repos"] = sum(1 for p in CACHE_DIR.iterdir() if p.is_dir())

    # Count stored skills
    if STORE_DIR.exists():
        report["stored_skills"] = sum(1 for p in STORE_DIR.iterdir() if p.is_dir())

    # Check symlinks in agent directories
    for agent_dir in agent_dirs:
        if not agent_dir.exists():
            continue
        for child in agent_dir.iterdir():
            if child.is_symlink():
                if not child.resolve().exists():
                    report["broken_links"].append(str(child))
                else:
                    report["healthy_links"] += 1
            elif child.is_dir():
                report["healthy_links"] += 1

    return report
