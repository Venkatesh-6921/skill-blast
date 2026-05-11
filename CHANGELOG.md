# Changelog

All notable changes to skill-blast are documented here.  
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

## [1.0.1] — 2026-05-11

### Fixed
- Fixed `UnicodeEncodeError` crashes on Windows by enforcing `utf-8` on stdout/stderr.
- Fixed integration test crashes on Windows CI by forcing `utf-8` decoding in subprocesses.
- Skipped symlink creation tests on Windows CI runners missing Developer Mode.
- Updated `actions/checkout` to v5 and `actions/setup-python` to v6 in CI pipelines.
### Added
- `--uninstall` flag to remove installed skills from agent directories
- `--check` flag for health diagnostics (broken symlinks, cache/store status, git connectivity)
- `--version` flag to print current version
- Integration tests for installer logic (mocked filesystem + subprocess)
- Agent detection tests
- Troubleshooting guide in README
- Management commands section in README
- `--info <ID>` flag to show detailed skill metadata
- `CODE_OF_CONDUCT.md` for the community
- CLI integration tests (`tests/test_cli_integration.py`)
- Social preview image for GitHub sharing

### Changed
- Replaced `YOUR_USERNAME` placeholder with `Venkatesh-6921` in all files

## [1.0.0] — 2026-05-10

### Added
- 50 curated AI agent skills across 9 categories
- Interactive wizard for non-developers (no flags needed)
- Auto-detection for 8 agents: Claude Code, OpenCode, Antigravity, Gemini CLI, Cursor, Windsurf, Continue.dev, Aider
- Cross-platform: Linux, macOS, Windows
- One-liner installers: `install.sh`, `install.ps1`, `install.bat`
- PyPI package: `pip install skill-blast`
- `--dry-run`, `--update`, `--list`, `--only`, `--skip`, `--agents` flags
- Symlink-based install on Linux/macOS (copy-based on Windows)
- Central skill store at `~/.skill-blast/` shared across all agents
- Rich TUI with progress bar, live status, summary table
