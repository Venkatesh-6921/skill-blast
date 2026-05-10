import subprocess
import sys
from pathlib import Path

def test_cli_version():
    result = subprocess.run(
        [sys.executable, "-m", "skill_blast", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "skill-blast" in result.stdout

def test_cli_list():
    result = subprocess.run(
        [sys.executable, "-m", "skill_blast", "--list"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "frontend-design" in result.stdout
    assert "Total: 50 skills" in result.stdout

def test_cli_info_valid():
    result = subprocess.run(
        [sys.executable, "-m", "skill_blast", "--info", "1"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "frontend-design" in result.stdout
    assert "Repository" in result.stdout

def test_cli_info_invalid():
    result = subprocess.run(
        [sys.executable, "-m", "skill_blast", "--info", "999"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "Error: Skill ID 999 not found" in result.stdout

def test_cli_dry_run():
    result = subprocess.run(
        [sys.executable, "-m", "skill_blast", "--dry-run", "--only", "Health", "--agents", "claude-code"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "DRY RUN — no files will be written" in result.stdout
    assert "personal-health" in result.stdout
