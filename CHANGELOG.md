# Changelog

All notable changes to skill-blast are documented here.  
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

## [3.0.0] — 2026-05-13

### Changed

- **Production/Stable Status**: Promoted package from Beta to Stable.
- **CI Hardening**: Bumped coverage gate to 70%+ (excluding interactive UI), added Python 3.13 support, and integrated Ruff linting.
- **Reliability**: Implemented atomic writes for registry and custom skills to prevent file corruption.
- **Observability**: Added `--verbose` flag for structured debug logging.
- **UX**: Updated installers to prefer `uv` for 10x faster installations.

## [2.2.1] — 2026-05-13

### Added

- **GitHub-based skill installation**: New `--github-install <ID>` flag installs skills directly from GitHub with full instruction parsing and sub-agent detection.
- **Multi-agent support**: Skills are automatically installed to all supported AI agent CLIs based on instruction files (SKILL.md, CLAUDE.md, AGENTS.md) found in the original repository.
- **Intelligent sub-agent parsing**: When a skill bundles or depends on sub-agents, they are automatically identified and installed alongside the parent skill.
- **Local install registry**: All installations/uninstalls are now tracked in `~/.skill-blast/registry.json` with timestamps and agent info.
- **Install status command**: New `--status` flag shows all installed skills from the local registry with agent and timestamp details.
- **Offline skill catalog**: All 50 skills bundled as `skill_blast/data/skills.json` for instant browsing without network access.
- **42 new tests**: Comprehensive test coverage for GitHub installation, sub-agent parsing, multi-agent distribution, registry tracking, offline mode, and backward compatibility (81 total tests, 0 failures).

### New Files

- `skill_blast/github_installer.py` — GitHub-based installer with instruction parsing
- `skill_blast/registry.py` — Local install/uninstall tracking
- `skill_blast/data/skills.json` — Bundled offline skill metadata
- `tests/test_github_installer.py` — 42 new tests

## [2.1.3] — 2026-05-11

### Fixed

- **TUI Layout Fix**: Resolved empty `DataTable` rendering inside `TabbedContent`. The internal `ContentSwitcher` widget lacked an explicit `height` constraint, causing all tab panes to collapse to zero height. Added proper CSS layout chain (`Screen → TabbedContent → ContentSwitcher → TabPane → DataTable`, all `1fr`).
- **Data Population Timing**: Moved `DataTable` row population from `compose()` to `on_mount()` to ensure widgets are fully initialized before receiving data.

## [2.1.2] — 2026-05-11

### Fixed

- **TUI Bugfix**: Resolved `BadIdentifier` error in the interactive list. The category `UI/Design` was causing an invalid widget ID because it contained a `/`. Tab IDs are now properly sanitized.

## [2.1.1] — 2026-05-11

### Fixed

- **CI/Headless Support**: Added a TTY check to the `--list` command. If the environment is non-interactive (like GitHub Actions), `skill-blast` now automatically falls back to a static list output instead of launching the full-screen TUI.

## [2.1.0] — 2026-05-11

### Added

- **Interactive TUI for `--list`**: Replaced the static list output with a full-screen interactive TUI built with `Textual`. Use `Tab` or mouse clicks to switch between category tabs, and arrow keys to scroll through skills.
- **New Dependency**: Added `textual>=0.80.0` for the interactive terminal interface.

## [2.0.3] — 2026-05-11

### Changed

- **List UI Upgrade**: The `skill-blast --list` command now outputs a beautiful, category-grouped multi-table layout instead of a single massive table. The `Repo` identifier has been merged directly underneath the `Skill Name`, making descriptions much easier to read without dense horizontal text wrapping.

## [2.0.2] — 2026-05-11

### Fixed

- **Concurrent Git Conflicts**: Resolved errors such as `Another git process seems to be running in this repository` and random command failures caused by multi-threaded `git fetch/reset` operations simultaneously targeting the same locally cached GitHub repository when multiple skills exist in a single repository. Implemented per-repository thread locks (`_REPO_LOCKS`) and an `UPDATED_REPOS` cache.

## [2.0.1] — 2026-05-11

### Fixed

- **Permission Denied Error**: Resolved `[Errno 13] Permission denied` errors during `--update` by correctly ignoring `.git` directories when copying from cache to central store.
- **Fast-forward Error**: Resolved `fatal: Cannot fast-forward to multiple branches` error by using explicit `git fetch` and `git reset --hard FETCH_HEAD` instead of `git pull --ff-only`.

## [2.0.0] — 2026-05-11

### Added

- **Frontmatter Auto-Injector**: Solved Claude Code ignoring 24 skills by auto-generating YAML frontmatter dynamically. All 50 skills are now visible in Claude Code.
- **Interactive Terminal UI**: Added a sleek, interactive multi-select TUI powered by `questionary` when running without flags.
- **Custom Skill Adder**: Added `--add <github-repo>` flag so users can inject arbitrary GitHub repositories into their local skill-blast database persistently.
- **Update with Safe Backup**: `--update` now properly pulls the newest branch and writes a `SKILL.md.bak` file before overwriting, protecting local user tweaks.

## [1.1.1] — 2026-05-11

### Fixed

- Fixed 8 skills that were pointing to "awesome-list" repos instead of the actual skill repositories (`nothing-design`, `dev-browser`, `generative-media`, `design-auditor`, `personal-health`, `dna-analysis`, `twitter-algorithm`, `competitive-ads`).

## [1.1.0] — 2026-05-11

### Added

- Concurrent multi-threaded skill installation (8 threads) — ~5x faster downloads.
- Dynamic `M/N` progress counter (e.g. `21/50`) during install and uninstall.

### Changed

- Thread-safe `FAILED_REPOS` tracking with `threading.Lock` in installer module.

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
