# Contributing to skill-blast

Thanks for helping make skill-blast better! Here's everything you need.

---

## Ways to contribute

- **Add a new skill** — found a great one not in the list?
- **Fix a broken repo** — skill URLs change; PRs to update are always welcome
- **Improve detection** — better agent auto-detection for any platform
- **Bug reports** — open an issue with your OS + Python version

---

## Adding a new skill

1. **Fork** the repo and clone your fork
2. Open `skill_blast/skills.py`
3. Add a `Skill(...)` entry to `ALL_SKILLS`:

```python
Skill(
    id=51,                              # next available ID
    name="my-skill-name",              # slug, used as folder name (no spaces)
    repo="github-owner/repo-name",     # GitHub owner/repo
    subpath="path/to/skill/dir",       # None if the whole repo is the skill
    desc="One-line description",       # shown in --list and progress bar
    category="Engineering",            # must match an existing category
    tags=["tag1", "tag2"],             # searchable tags (future use)
),
```

4. **Verify the `subpath`** (important!):

   If the skill lives inside a larger repo (e.g., `anthropics/skills` → `skills/frontend-design`):
   ```bash
   # Clone the repo and check the subpath exists
   git clone --depth=1 https://github.com/owner/repo /tmp/test-repo
   ls /tmp/test-repo/path/to/skill/   # should contain SKILL.md or similar
   rm -rf /tmp/test-repo
   ```
   If the entire repo *is* the skill, set `subpath=None`.

5. **Test locally:**

```bash
pip install -e .
skill-blast --dry-run --only Engineering   # check it appears in list
skill-blast --list --only Engineering      # verify metadata looks right
skill-blast --only Engineering             # actually install
skill-blast --check                        # verify symlinks are healthy
```

6. **Run the test suite:**

```bash
pytest tests/ -v
```

7. Open a PR with:
   - The `skills.py` change
   - A one-line note in `CHANGELOG.md` under `Unreleased`

---

## Categories

| Category | When to use |
|---|---|
| `UI/Design` | Anything about visual output, CSS, color, diagrams |
| `Content` | Social media, posts, hooks, publishing |
| `Writing` | Prose style, editing, humanizing |
| `Research` | Information gathering, synthesis, citations |
| `Marketing` | SEO, CRO, email, ads, copywriting |
| `Product` | PM frameworks, JTBD, strategy |
| `Engineering` | Code quality, tooling, automation |
| `Media` | Video, audio, generative media |
| `Health` | Medical, wellness, personal data |

---

## Git workflow

> **⚠️ Direct pushes to `main` are not allowed.** All changes go through pull requests.

### For every change — no matter how small:

```bash
# 1. Create a branch from latest main
git checkout main && git pull
git checkout -b fix/short-description     # or feat/, docs/, refactor/

# 2. Make your changes, then test locally
pytest tests/ -v
SKILLBLAST_NO_TUI=1 skill-blast --list    # smoke test

# 3. Commit
git add -A
git commit -m "fix: what you changed and why"

# 4. Push your branch (never main)
git push origin fix/short-description

# 5. Open a Pull Request
gh pr create --title "fix: short description" --body "Explain the change"
# or go to github.com/Venkatesh-6921/skill-blast and click "Compare & pull request"
```

### Branch naming

| Prefix | Use for |
|---|---|
| `fix/` | Bug fixes |
| `feat/` | New features or skills |
| `docs/` | Documentation only |
| `refactor/` | Code restructuring (no behavior change) |

### Releases (maintainers only)

Version bumps and PyPI releases happen on `main` after PRs are merged:

```bash
# After merging a PR, on main:
git tag v2.x.x
git push origin main --tags    # triggers PyPI publish via CI
```

---

## Development setup

```bash
git clone https://github.com/Venkatesh-6921/skill-blast
cd skill-blast
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

---

## Code style

- Python 3.9+ compatible
- Dependencies: `rich`, `textual`, `questionary` — keep it minimal
- Keep `installer.py` pure — no UI code there
- All new platform logic goes in `agents.py`

---

## Reporting a broken skill

Open an issue with title: `[broken] skill-name` and include:
- Error message from skill-blast
- Output of `git clone https://github.com/owner/repo --depth=1` run manually

---

## License

By contributing, you agree your changes are licensed under MIT.
