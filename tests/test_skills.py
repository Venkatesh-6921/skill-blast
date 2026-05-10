"""Basic sanity tests — no git required, no network calls."""

import pytest
from skill_blast.skills import ALL_SKILLS, SKILLS_BY_ID, CATEGORIES, CATEGORY_COLORS
from skill_blast.agents import AGENTS


class TestSkillData:
    def test_fifty_skills_loaded(self):
        assert len(ALL_SKILLS) == 50

    def test_all_ids_unique(self):
        ids = [s.id for s in ALL_SKILLS]
        assert len(ids) == len(set(ids)), "Duplicate skill IDs found"

    def test_all_names_unique(self):
        names = [s.name for s in ALL_SKILLS]
        assert len(names) == len(set(names)), "Duplicate skill names found"

    def test_all_categories_have_color(self):
        for s in ALL_SKILLS:
            assert s.category in CATEGORY_COLORS, f"Category '{s.category}' missing from CATEGORY_COLORS"

    def test_all_repos_nonempty(self):
        for s in ALL_SKILLS:
            assert s.repo and "/" in s.repo, f"Skill {s.id} has invalid repo: {s.repo}"

    def test_all_descs_nonempty(self):
        for s in ALL_SKILLS:
            assert s.desc.strip(), f"Skill {s.id} has empty description"

    def test_skills_by_id_lookup(self):
        for s in ALL_SKILLS:
            assert SKILLS_BY_ID[s.id] is s

    def test_clone_url_format(self):
        for s in ALL_SKILLS:
            assert s.clone_url.startswith("https://github.com/")
            assert s.clone_url.endswith(".git")

    def test_categories_list(self):
        assert len(CATEGORIES) > 0
        for cat in CATEGORIES:
            assert isinstance(cat, str)


class TestAgents:
    def test_agents_have_required_keys(self):
        required = {"name", "icon", "skills_dir", "detect", "docs", "note"}
        for key, agent in AGENTS.items():
            missing = required - set(agent.keys())
            assert not missing, f"Agent '{key}' missing keys: {missing}"

    def test_detect_is_callable(self):
        for key, agent in AGENTS.items():
            assert callable(agent["detect"]), f"Agent '{key}' detect is not callable"

    def test_skills_dir_is_path(self):
        from pathlib import Path
        for key, agent in AGENTS.items():
            assert isinstance(agent["skills_dir"], Path), f"Agent '{key}' skills_dir is not a Path"


class TestCLIImport:
    def test_cli_importable(self):
        from skill_blast.cli import main
        assert callable(main)

    def test_installer_importable(self):
        from skill_blast.installer import install_skill, ensure_repo, check_git
        assert callable(install_skill)
        assert callable(ensure_repo)
        assert callable(check_git)
