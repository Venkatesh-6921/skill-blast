"""
Tests for GitHub-based installation, sub-agent parsing, multi-agent support,
and the local registry system.

Covers items from implementation plan sections 4.3 and 4.4:
- GitHub installation: CLI successfully pulls and installs skills from GitHub
- Sub-agent parsing: Sub-agents are correctly identified from repo instructions
- Multi-agent installation: Skills are distributed to all supported AI agent CLIs
- Registry: install/uninstall updates registry.json
- Offline mode: skills.json loads without network
- Backward compat: all existing CLI flags still work
"""

import json
import platform
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from skill_blast.skills import ALL_SKILLS, Skill, SKILLS_BY_ID
from skill_blast.agents import AGENTS


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def sample_skill():
    return Skill(
        id=999,
        name="test-skill",
        repo="test-org/test-repo",
        subpath=None,
        desc="A test skill",
        category="Engineering",
        tags=["test"],
    )


@pytest.fixture
def sample_skill_with_subpath():
    return Skill(
        id=998,
        name="test-sub-skill",
        repo="test-org/multi-repo",
        subpath="skills/sub-skill",
        desc="A test skill with subpath",
        category="Engineering",
        tags=["test", "subpath"],
    )


@pytest.fixture
def mock_agent_dirs(tmp_path):
    """Create temporary agent directories for claude-code and opencode."""
    dirs = []
    for agent in ["claude", "opencode"]:
        skills_dir = tmp_path / f".{agent}" / "skills"
        skills_dir.mkdir(parents=True)
        dirs.append(skills_dir)
    return dirs


@pytest.fixture
def mock_registry(tmp_path):
    """Create a temporary registry file for testing."""
    registry_file = tmp_path / ".skill-blast" / "registry.json"
    registry_file.parent.mkdir(parents=True, exist_ok=True)
    return registry_file


@pytest.fixture
def instruction_with_sub_agents():
    """Sample instruction content that references sub-agents."""
    return """---
name: social-media-os
description: The full system behind 350K followers — 17 skills
---

# Social Media OS

This skill bundles multiple sub-agents for a complete social media workflow.

## Sub-agents:

- voice-builder
- reels-scripting
- post-scorer
- youtube-thumbnail
- hook-generator

## Installation

Works with Claude Code, OpenCode, and Cursor.

Copy the skill directory to `~/.claude/skills/` or `~/.opencode/skills/`.
"""


@pytest.fixture
def instruction_claude_only():
    """Sample instruction content targeting only Claude Code."""
    return """---
name: frontend-design
description: Beautiful frontend designs
---

# Frontend Design Skill

This skill is designed for Claude Code.

## Installation

1. Copy to `~/.claude/skills/frontend-design/`
2. Load via /skills in Claude Code
"""


@pytest.fixture
def instruction_no_agents():
    """Sample instruction content with no specific agent mentions."""
    return """---
name: generic-skill
description: A generic skill
---

# Generic Skill

This skill does something useful.
No specific agent setup required.
"""


# ══════════════════════════════════════════════════════════════════════════════
# Section 4.3 Feature Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestGitHubHostedSkills:
    """GitHub-hosted skills: skills.json is bundled and loadable offline."""

    def test_skills_json_exists(self):
        """skills.json should be bundled in the package data directory."""
        skills_json = Path(__file__).parent.parent / "skill_blast" / "data" / "skills.json"
        assert skills_json.exists(), "skills.json not found in skill_blast/data/"

    def test_skills_json_valid(self):
        """skills.json should be valid JSON with all 50 skills."""
        skills_json = Path(__file__).parent.parent / "skill_blast" / "data" / "skills.json"
        data = json.loads(skills_json.read_text(encoding="utf-8"))
        assert isinstance(data, list)
        assert len(data) == 50

    def test_skills_json_schema(self):
        """Each skill entry should have the required fields."""
        skills_json = Path(__file__).parent.parent / "skill_blast" / "data" / "skills.json"
        data = json.loads(skills_json.read_text(encoding="utf-8"))
        required_keys = {"id", "name", "repo", "subpath", "desc", "category", "tags"}
        for entry in data:
            missing = required_keys - set(entry.keys())
            assert not missing, f"Skill {entry.get('name', '?')} missing keys: {missing}"

    def test_skills_json_matches_hardcoded(self):
        """skills.json should match the hardcoded ALL_SKILLS list."""
        skills_json = Path(__file__).parent.parent / "skill_blast" / "data" / "skills.json"
        data = json.loads(skills_json.read_text(encoding="utf-8"))
        json_ids = sorted(s["id"] for s in data)
        code_ids = sorted(s.id for s in ALL_SKILLS)
        assert json_ids == code_ids, "skills.json IDs don't match ALL_SKILLS"

    def test_skills_json_offline_load(self):
        """Skills should be loadable from JSON without any network calls."""
        skills_json = Path(__file__).parent.parent / "skill_blast" / "data" / "skills.json"
        data = json.loads(skills_json.read_text(encoding="utf-8"))
        loaded_skills = [Skill(**entry) for entry in data]
        assert len(loaded_skills) == 50
        assert all(isinstance(s, Skill) for s in loaded_skills)


class TestDirectGitHubInstallation:
    """Direct GitHub installation: CLI installs skills from GitHub repos."""

    def test_install_from_github_importable(self):
        from skill_blast.github_installer import install_from_github
        assert callable(install_from_github)

    def test_uninstall_from_github_importable(self):
        from skill_blast.github_installer import uninstall_from_github
        assert callable(uninstall_from_github)

    @patch("skill_blast.installer.install_skill")
    @patch("skill_blast.installer.ensure_repo")
    @patch("skill_blast.registry.register_install")
    @patch("skill_blast.github_installer.detect_agents")
    def test_install_from_github_success(
        self, mock_detect, mock_register, mock_ensure, mock_install, sample_skill
    ):
        """install_from_github should clone the repo and install the skill."""
        mock_ensure.return_value = (True, "cached")
        mock_install.return_value = {"ok": True, "linked": ["claude"], "already": [], "error": None}
        mock_detect.return_value = {"claude-code": AGENTS["claude-code"]}

        from skill_blast.github_installer import install_from_github

        with patch("skill_blast.installer.CACHE_DIR", Path("/tmp/fake-cache")), \
             patch("skill_blast.github_installer.read_instruction_file", return_value=None):
            result = install_from_github(sample_skill, agent_keys=["claude-code"])

        assert result["ok"] is True
        assert "claude-code" in result["agents_resolved"]
        mock_ensure.assert_called_once_with(sample_skill.repo, update=False)

    @patch("skill_blast.installer.ensure_repo")
    def test_install_from_github_repo_failure(self, mock_ensure, sample_skill):
        """Should fail gracefully when GitHub fetch fails."""
        mock_ensure.return_value = (False, "network error")

        from skill_blast.github_installer import install_from_github

        result = install_from_github(sample_skill, agent_keys=["claude-code"])
        assert result["ok"] is False
        assert "GitHub fetch failed" in result["error"]

    @patch("skill_blast.installer.install_skill")
    @patch("skill_blast.installer.ensure_repo")
    @patch("skill_blast.registry.register_install")
    @patch("skill_blast.github_installer.detect_agents")
    def test_install_from_github_dry_run(
        self, mock_detect, mock_register, mock_ensure, mock_install, sample_skill
    ):
        """Dry run should not call ensure_repo or register."""
        mock_install.return_value = {"ok": True, "linked": ["claude(dry)"], "already": [], "error": None}
        mock_detect.return_value = {"claude-code": AGENTS["claude-code"]}

        from skill_blast.github_installer import install_from_github

        result = install_from_github(sample_skill, agent_keys=["claude-code"], dry_run=True)
        assert result["ok"] is True
        mock_ensure.assert_not_called()
        mock_register.assert_not_called()


class TestIntelligentInstructionParsing:
    """Intelligent instruction parsing: sub-agents are detected and installed."""

    def test_parse_instruction_file_importable(self):
        from skill_blast.github_installer import parse_instruction_file
        assert callable(parse_instruction_file)

    def test_parse_detects_sub_agents(self, instruction_with_sub_agents):
        from skill_blast.github_installer import parse_instruction_file

        parsed = parse_instruction_file(instruction_with_sub_agents)
        assert parsed["has_sub_agents"] is True
        assert len(parsed["sub_agent_names"]) > 0

    def test_parse_detects_claude_agent(self, instruction_claude_only):
        from skill_blast.github_installer import parse_instruction_file

        parsed = parse_instruction_file(instruction_claude_only)
        assert "claude-code" in parsed["supported_agents"]

    def test_parse_detects_multiple_agents(self, instruction_with_sub_agents):
        from skill_blast.github_installer import parse_instruction_file

        parsed = parse_instruction_file(instruction_with_sub_agents)
        # The fixture mentions Claude Code, OpenCode, and Cursor
        assert "claude-code" in parsed["supported_agents"]
        assert "opencode" in parsed["supported_agents"]
        assert "cursor" in parsed["supported_agents"]

    def test_parse_no_agents_detected(self, instruction_no_agents):
        from skill_blast.github_installer import parse_instruction_file

        parsed = parse_instruction_file(instruction_no_agents)
        assert parsed["supported_agents"] == []
        assert parsed["has_sub_agents"] is False

    def test_parse_empty_content(self):
        from skill_blast.github_installer import parse_instruction_file

        parsed = parse_instruction_file("")
        assert parsed["supported_agents"] == []
        assert parsed["has_sub_agents"] is False
        assert parsed["sub_agent_names"] == []

    def test_parse_none_content(self):
        from skill_blast.github_installer import parse_instruction_file

        parsed = parse_instruction_file(None)
        assert parsed["supported_agents"] == []

    def test_read_instruction_file_priority(self, tmp_path):
        """SKILL.md should be preferred over README.md."""
        from skill_blast.github_installer import read_instruction_file

        (tmp_path / "README.md").write_text("# README", encoding="utf-8")
        (tmp_path / "SKILL.md").write_text("# SKILL", encoding="utf-8")

        content = read_instruction_file(tmp_path)
        assert content == "# SKILL"

    def test_read_instruction_file_fallback(self, tmp_path):
        """Should fall back to README.md if no SKILL.md exists."""
        from skill_blast.github_installer import read_instruction_file

        (tmp_path / "README.md").write_text("# Fallback README", encoding="utf-8")

        content = read_instruction_file(tmp_path)
        assert content == "# Fallback README"

    def test_read_instruction_file_none(self, tmp_path):
        """Should return None if no instruction file exists."""
        from skill_blast.github_installer import read_instruction_file

        content = read_instruction_file(tmp_path)
        assert content is None


class TestMultiAgentSupport:
    """Multi-agent support: skills are installed to all supported agent CLIs."""

    def test_resolve_target_agents_explicit(self, sample_skill):
        """Explicitly specified agents should override detection."""
        from skill_blast.github_installer import resolve_target_agents

        agents = resolve_target_agents(sample_skill, explicit_agents=["claude-code", "opencode"])
        assert agents == ["claude-code", "opencode"]

    def test_resolve_target_agents_from_instructions(self, sample_skill, instruction_claude_only):
        """Should resolve agents from instruction file when available."""
        from skill_blast.github_installer import resolve_target_agents

        with patch("skill_blast.github_installer.detect_agents") as mock_detect:
            mock_detect.return_value = {"claude-code": AGENTS["claude-code"]}
            agents = resolve_target_agents(sample_skill, instruction_content=instruction_claude_only)
            assert "claude-code" in agents

    def test_resolve_target_agents_default_detected(self, sample_skill):
        """Should fall back to all detected agents when no instructions."""
        from skill_blast.github_installer import resolve_target_agents

        with patch("skill_blast.github_installer.detect_agents") as mock_detect:
            mock_detect.return_value = {
                "claude-code": AGENTS["claude-code"],
                "cursor": AGENTS["cursor"],
            }
            agents = resolve_target_agents(sample_skill)
            assert "claude-code" in agents
            assert "cursor" in agents

    def test_resolve_target_agents_empty_detection(self, sample_skill):
        """Should default to claude-code when nothing is detected."""
        from skill_blast.github_installer import resolve_target_agents

        with patch("skill_blast.github_installer.detect_agents") as mock_detect:
            mock_detect.return_value = {}
            agents = resolve_target_agents(sample_skill)
            assert agents == ["claude-code"]

    def test_resolve_target_agents_invalid_key_ignored(self, sample_skill):
        """Invalid agent keys should be filtered out."""
        from skill_blast.github_installer import resolve_target_agents

        agents = resolve_target_agents(
            sample_skill, explicit_agents=["claude-code", "nonexistent-agent"]
        )
        assert "claude-code" in agents
        assert "nonexistent-agent" not in agents

    def test_resolve_sub_agents(self, sample_skill, instruction_with_sub_agents):
        """Should resolve sub-agent names to Skill objects."""
        from skill_blast.github_installer import resolve_sub_agents

        sub_skills = resolve_sub_agents(sample_skill, instruction_with_sub_agents)
        # These sub-skill names are in ALL_SKILLS
        sub_names = [s.name for s in sub_skills]
        # voice-builder, reels-scripting, post-scorer, youtube-thumbnail, hook-generator
        # are all real skills in the catalog
        for expected in ["voice-builder", "reels-scripting", "post-scorer"]:
            assert expected in sub_names, f"Expected sub-agent '{expected}' not found"

    def test_resolve_sub_agents_none_content(self, sample_skill):
        """Should return empty list when no instruction content."""
        from skill_blast.github_installer import resolve_sub_agents

        sub_skills = resolve_sub_agents(sample_skill, None)
        assert sub_skills == []

    def test_get_install_status(self):
        """get_install_status should return a dict for every skill."""
        from skill_blast.github_installer import get_install_status

        with patch("skill_blast.registry.get_installed", return_value={}):
            status = get_install_status()
            assert len(status) == len(ALL_SKILLS)
            for skill in ALL_SKILLS:
                assert skill.name in status
                assert status[skill.name]["installed"] is False


# ══════════════════════════════════════════════════════════════════════════════
# Section 4.4 Test Items — Registry
# ══════════════════════════════════════════════════════════════════════════════


class TestRegistry:
    """Registry: install/uninstall updates registry.json."""

    def test_registry_importable(self):
        from skill_blast.registry import (
            register_install,
            register_uninstall,
            is_installed,
            get_installed,
            get_entry,
            clear_registry,
        )
        assert callable(register_install)
        assert callable(register_uninstall)

    def test_register_install(self, tmp_path):
        from skill_blast import registry

        reg_file = tmp_path / "registry.json"
        with patch.object(registry, "REGISTRY_FILE", reg_file):
            registry.register_install("test-skill", 999, ["claude-code"])

            assert reg_file.exists()
            data = json.loads(reg_file.read_text(encoding="utf-8"))
            assert "test-skill" in data
            assert data["test-skill"]["skill_id"] == 999
            assert "claude-code" in data["test-skill"]["agents"]

    def test_register_uninstall(self, tmp_path):
        from skill_blast import registry

        reg_file = tmp_path / "registry.json"
        with patch.object(registry, "REGISTRY_FILE", reg_file):
            # First install, then uninstall
            registry.register_install("test-skill", 999, ["claude-code"])
            assert registry.is_installed("test-skill")

            registry.register_uninstall("test-skill")
            assert not registry.is_installed("test-skill")

    def test_register_preserves_install_date(self, tmp_path):
        from skill_blast import registry

        reg_file = tmp_path / "registry.json"
        with patch.object(registry, "REGISTRY_FILE", reg_file):
            registry.register_install("test-skill", 999, ["claude-code"])
            first_install = json.loads(reg_file.read_text())["test-skill"]["installed_at"]

            # Re-install (update) should preserve installed_at
            registry.register_install("test-skill", 999, ["claude-code", "opencode"])
            second_data = json.loads(reg_file.read_text())["test-skill"]
            assert second_data["installed_at"] == first_install
            assert "opencode" in second_data["agents"]

    def test_get_installed_empty(self, tmp_path):
        from skill_blast import registry

        reg_file = tmp_path / "nonexistent" / "registry.json"
        with patch.object(registry, "REGISTRY_FILE", reg_file):
            assert registry.get_installed() == {}

    def test_get_entry(self, tmp_path):
        from skill_blast import registry

        reg_file = tmp_path / "registry.json"
        with patch.object(registry, "REGISTRY_FILE", reg_file):
            registry.register_install("my-skill", 42, ["cursor"])
            entry = registry.get_entry("my-skill")
            assert entry is not None
            assert entry["skill_id"] == 42

            assert registry.get_entry("not-here") is None

    def test_clear_registry(self, tmp_path):
        from skill_blast import registry

        reg_file = tmp_path / "registry.json"
        with patch.object(registry, "REGISTRY_FILE", reg_file):
            registry.register_install("test-skill", 999, ["claude-code"])
            assert reg_file.exists()

            registry.clear_registry()
            assert not reg_file.exists()

    def test_corrupt_registry_handled(self, tmp_path):
        """Corrupt registry.json should not crash — return empty dict."""
        from skill_blast import registry

        reg_file = tmp_path / "registry.json"
        reg_file.write_text("NOT VALID JSON {{{", encoding="utf-8")

        with patch.object(registry, "REGISTRY_FILE", reg_file):
            assert registry.get_installed() == {}
            assert registry.is_installed("anything") is False


# ══════════════════════════════════════════════════════════════════════════════
# Section 4.4 — Offline mode
# ══════════════════════════════════════════════════════════════════════════════


class TestOfflineMode:
    """Offline mode: skills.json loads without network."""

    def test_skills_json_loads_without_network(self):
        """Loading skills from JSON should work without any network calls."""
        skills_json = Path(__file__).parent.parent / "skill_blast" / "data" / "skills.json"
        data = json.loads(skills_json.read_text(encoding="utf-8"))
        skills = [Skill(**entry) for entry in data]
        assert len(skills) == 50

    def test_all_skill_ids_in_json(self):
        """Every hardcoded skill ID should exist in skills.json."""
        skills_json = Path(__file__).parent.parent / "skill_blast" / "data" / "skills.json"
        data = json.loads(skills_json.read_text(encoding="utf-8"))
        json_ids = {s["id"] for s in data}
        for skill in ALL_SKILLS:
            assert skill.id in json_ids, f"Skill {skill.name} (ID {skill.id}) missing from skills.json"


# ══════════════════════════════════════════════════════════════════════════════
# Section 4.4 — Backward compatibility
# ══════════════════════════════════════════════════════════════════════════════


class TestBackwardCompat:
    """Backward compat: all existing CLI flags still work."""

    def test_existing_imports_still_work(self):
        """All v2 imports should still function."""
        from skill_blast.cli import main, run_install, run_uninstall, cmd_list, cmd_info, cmd_check
        from skill_blast.installer import install_skill, uninstall_skill, health_check
        from skill_blast.skills import ALL_SKILLS, SKILLS_BY_ID, CATEGORIES
        from skill_blast.agents import AGENTS, detect_agents

        assert callable(main)
        assert callable(run_install)
        assert callable(install_skill)
        assert len(ALL_SKILLS) == 50

    def test_new_imports_available(self):
        """New v3 modules should be importable."""
        from skill_blast.github_installer import (
            install_from_github,
            uninstall_from_github,
            parse_instruction_file,
            resolve_target_agents,
            resolve_sub_agents,
            get_install_status,
        )
        from skill_blast.registry import (
            register_install,
            register_uninstall,
            is_installed,
            get_installed,
        )

        assert callable(install_from_github)
        assert callable(register_install)

    def test_skill_dataclass_unchanged(self):
        """Skill dataclass should retain all v2 fields."""
        skill = ALL_SKILLS[0]
        assert hasattr(skill, "id")
        assert hasattr(skill, "name")
        assert hasattr(skill, "repo")
        assert hasattr(skill, "subpath")
        assert hasattr(skill, "desc")
        assert hasattr(skill, "category")
        assert hasattr(skill, "tags")
        assert hasattr(skill, "repo_url")
        assert hasattr(skill, "clone_url")

    def test_agents_dict_unchanged(self):
        """Agent definitions should retain all v2 keys."""
        required = {"name", "icon", "skills_dir", "detect", "docs", "note"}
        for key, agent in AGENTS.items():
            missing = required - set(agent.keys())
            assert not missing, f"Agent '{key}' missing keys: {missing}"
