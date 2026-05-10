"""Integration tests for installer — uses mocked filesystem and subprocess."""

import platform
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from skill_blast.installer import (
    install_skill,
    uninstall_skill,
    health_check,
    check_git,
    ensure_repo,
    CACHE_DIR,
    STORE_DIR,
)
from skill_blast.skills import ALL_SKILLS, Skill


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
def mock_agent_dirs(tmp_path):
    """Create temporary agent directories."""
    dirs = []
    for agent in ["claude", "opencode"]:
        skills_dir = tmp_path / f".{agent}" / "skills"
        skills_dir.mkdir(parents=True)
        dirs.append(skills_dir)
    return dirs


# ── Git helpers ───────────────────────────────────────────────────────────────

class TestCheckGit:
    def test_git_available(self):
        ok, msg = check_git()
        # git should be available in test environments
        assert isinstance(ok, bool)
        assert isinstance(msg, str)

    @patch("skill_blast.installer.subprocess.run")
    def test_git_not_found(self, mock_run):
        mock_run.side_effect = FileNotFoundError
        ok, msg = check_git()
        assert ok is False
        assert "git not found" in msg


class TestEnsureRepo:
    @patch("skill_blast.installer._clone")
    def test_clone_new_repo(self, mock_clone, tmp_path):
        mock_clone.return_value = (True, "ok")
        with patch("skill_blast.installer.CACHE_DIR", tmp_path / "cache"):
            ok, msg = ensure_repo("test/repo")
            assert ok is True
            mock_clone.assert_called_once()

    @patch("skill_blast.installer._pull")
    def test_update_existing_repo(self, mock_pull, tmp_path):
        mock_pull.return_value = (True, "Already up to date.")
        cache = tmp_path / "cache"
        repo_dir = cache / "test__repo"
        repo_dir.mkdir(parents=True)
        with patch("skill_blast.installer.CACHE_DIR", cache):
            ok, msg = ensure_repo("test/repo", update=True)
            assert ok is True
            assert "updated" in msg

    def test_cached_repo_skip_clone(self, tmp_path):
        cache = tmp_path / "cache"
        repo_dir = cache / "test__repo"
        repo_dir.mkdir(parents=True)
        with patch("skill_blast.installer.CACHE_DIR", cache):
            ok, msg = ensure_repo("test/repo")
            assert ok is True
            assert msg == "cached"


# ── Install skill ─────────────────────────────────────────────────────────────

class TestInstallSkill:
    def test_dry_run(self, sample_skill, mock_agent_dirs):
        result = install_skill(sample_skill, mock_agent_dirs, dry_run=True)
        assert result["ok"] is True
        assert result["repo_msg"] == "dry-run"
        assert len(result["linked"]) == len(mock_agent_dirs)

    @patch("skill_blast.installer.ensure_repo")
    def test_repo_failure_aborts(self, mock_ensure, sample_skill, mock_agent_dirs):
        mock_ensure.return_value = (False, "network error")
        result = install_skill(sample_skill, mock_agent_dirs)
        assert result["ok"] is False
        assert result["error"] == "network error"

    @patch("skill_blast.installer.ensure_repo")
    def test_install_creates_links(self, mock_ensure, sample_skill, mock_agent_dirs, tmp_path):
        mock_ensure.return_value = (True, "cached")
        # Create a fake cached repo
        cache = tmp_path / "cache"
        repo_dir = cache / "test-org__test-repo"
        repo_dir.mkdir(parents=True)
        (repo_dir / "SKILL.md").write_text("# Test")

        store = tmp_path / "store"

        with patch("skill_blast.installer.CACHE_DIR", cache), \
             patch("skill_blast.installer.STORE_DIR", store):
            result = install_skill(sample_skill, mock_agent_dirs)
            assert result["ok"] is True
            # Check that the central store was created
            assert (store / "test-skill").exists()


# ── Uninstall skill ───────────────────────────────────────────────────────────

class TestUninstallSkill:
    def test_uninstall_removes_links(self, sample_skill, mock_agent_dirs, tmp_path):
        # Pre-create symlinks/dirs
        store = tmp_path / "store"
        store_dest = store / "test-skill"
        store_dest.mkdir(parents=True)
        (store_dest / "SKILL.md").write_text("# Test")

        for agent_dir in mock_agent_dirs:
            link = agent_dir / "test-skill"
            link.symlink_to(store_dest)

        with patch("skill_blast.installer.STORE_DIR", store):
            result = uninstall_skill(sample_skill, mock_agent_dirs)
            assert result["ok"] is True
            assert len(result["removed"]) == len(mock_agent_dirs)
            # Symlinks should be gone
            for agent_dir in mock_agent_dirs:
                assert not (agent_dir / "test-skill").exists()
            # Central store should be removed
            assert not store_dest.exists()

    def test_uninstall_not_installed(self, sample_skill, mock_agent_dirs, tmp_path):
        with patch("skill_blast.installer.STORE_DIR", tmp_path / "store"):
            result = uninstall_skill(sample_skill, mock_agent_dirs)
            assert result["ok"] is True
            assert len(result["not_found"]) == len(mock_agent_dirs)


# ── Health check ──────────────────────────────────────────────────────────────

class TestHealthCheck:
    def test_empty_install(self, mock_agent_dirs, tmp_path):
        with patch("skill_blast.installer.CACHE_DIR", tmp_path / "cache"), \
             patch("skill_blast.installer.STORE_DIR", tmp_path / "store"):
            report = health_check(mock_agent_dirs)
            assert isinstance(report["git_ok"], bool)
            assert report["cache_exists"] is False
            assert report["store_exists"] is False
            assert report["cached_repos"] == 0
            assert report["stored_skills"] == 0
            assert report["broken_links"] == []

    def test_detects_broken_symlinks(self, mock_agent_dirs, tmp_path):
        # Create a broken symlink
        broken = mock_agent_dirs[0] / "dead-skill"
        broken.symlink_to(tmp_path / "nonexistent")

        with patch("skill_blast.installer.CACHE_DIR", tmp_path / "cache"), \
             patch("skill_blast.installer.STORE_DIR", tmp_path / "store"):
            report = health_check(mock_agent_dirs)
            assert len(report["broken_links"]) == 1
            assert "dead-skill" in report["broken_links"][0]

    def test_counts_healthy_links(self, mock_agent_dirs, tmp_path):
        # Create a valid directory (simulates a Windows copy-based install)
        skill_dir = mock_agent_dirs[0] / "good-skill"
        skill_dir.mkdir()

        with patch("skill_blast.installer.CACHE_DIR", tmp_path / "cache"), \
             patch("skill_blast.installer.STORE_DIR", tmp_path / "store"):
            report = health_check(mock_agent_dirs)
            assert report["healthy_links"] >= 1
