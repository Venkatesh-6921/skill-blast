<div align="center">

# 🚀 skill-blast

![skill-blast banner](https://raw.githubusercontent.com/Venkatesh-6921/skill-blast/main/docs/social-preview.png)

**One-click installer for 50 top AI agent skills**

[![PyPI version](https://img.shields.io/pypi/v/skill-blast?color=cyan&style=flat-square&cache=none)](https://pypi.org/project/skill-blast/)
[![Python](https://img.shields.io/pypi/pyversions/skill-blast?style=flat-square&cache=none)](https://pypi.org/project/skill-blast/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Downloads](https://img.shields.io/badge/downloads-new-blue?style=flat-square)](https://pypi.org/project/skill-blast/)
[![OS: Windows, macOS, Linux](https://img.shields.io/badge/OS-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)](#installation)

Installs the **50 best community AI skills** into every agent you use —  
Claude Code, OpenCode, Antigravity, Gemini CLI, Cursor, Windsurf — in seconds.

**Works for everyone, including non-developers. No coding knowledge needed.**

</div>

---

## ✨ What it does

Clones the top community skills from GitHub and wires them into every AI agent on your machine — automatically.

```
skill-blast installs 50 skills across 9 categories:

  🎨 UI/Design    ·  9 skills  (frontend-design, canvas-design, color-expert…)
  📱 Content      · 10 skills  (social-media-os, voice-builder, reels-scripting…)
  ✍️  Writing      ·  2 skills  (humanizer, beautiful-prose)
  🔬 Research     ·  5 skills  (deep-research, academic-research, daydream…)
  📈 Marketing    ·  7 skills  (marketing-module, geo-seo, email-bible…)
  🗂️  Product      ·  3 skills  (pm-skills, jtbd-interview, ai-transformation)
  ⚙️  Engineering  ·  8 skills  (superpowers, repomix, antfu-skills…)
  🎬 Media        ·  4 skills  (remotion, ai-video-toolkit, ai-music…)
  🏥 Health       ·  2 skills  (personal-health, dna-analysis)
```

---

## 🖥️ Supported agents

| Agent | Auto-detected? | Skills directory |
|-------|---------------|-----------------|
| 🤖 **Claude Code** | ✅ | `~/.claude/skills/` |
| ⚡ **OpenCode** | ✅ | `~/.opencode/skills/` |
| 🚀 **Antigravity** | ✅ | `~/.antigravity/skills/` |
| ♊ **Gemini CLI** | ✅ | `~/.gemini/skills/` |
| 🖱️ **Cursor** | ✅ | `~/.cursor/skills/` |
| 🏄 **Windsurf** | ✅ | `~/.codeium/windsurf/skills/` |
| 🔄 **Continue.dev** | ✅ | `~/.continue/skills/` |
| ✏️ **Aider** | ✅ | `~/.aider/skills/` |

---

## 📦 Installation

### 🟢 Easiest — pip (all platforms)

```bash
pip install skill-blast
skill-blast
```

### 🐧 Linux / macOS — one-liner

```bash
curl -fsSL https://raw.githubusercontent.com/Venkatesh-6921/skill-blast/main/install.sh | bash
```

Or with wget:
```bash
wget -qO- https://raw.githubusercontent.com/Venkatesh-6921/skill-blast/main/install.sh | bash
```

### 🪟 Windows — PowerShell

```powershell
irm https://raw.githubusercontent.com/Venkatesh-6921/skill-blast/main/install.ps1 | iex
```

### 🪟 Windows — Double-click

1. Download [`install.bat`](install.bat)
2. Double-click it
3. Follow the prompts

### 🐍 From source

```bash
git clone https://github.com/Venkatesh-6921/skill-blast
cd skill-blast
pip install -e .
skill-blast
```

> **Requirements:** Python 3.9+ and git. That's it.

---

## 🧙 Usage

### Interactive wizard (recommended for beginners)

Just run with no arguments and follow the prompts:

```bash
skill-blast
```

```
Step 1 of 3 — Which AI agents do you use?

  Detected on your machine:
    ✓ 🤖 Claude Code
    ✓ ⚡ OpenCode

  All available agents:
    1. 🤖 Claude Code       detected
    2. ⚡ OpenCode          detected
    3. 🚀 Antigravity       not detected
    ...

  Your choice [1,2]:
```

### Developer — flags

```bash
# Install everything to auto-detected agents
skill-blast --all

# Target specific agents
skill-blast --agents claude-code opencode antigravity

# Install only specific categories
skill-blast --only Engineering "UI/Design" Research

# Skip specific skill IDs
skill-blast --skip 49 50

# Preview without writing any files
skill-blast --dry-run

# Pull latest for already-installed skills
skill-blast --update

# List all 50 skills
skill-blast --list

# List only one category
skill-blast --list --only Marketing

# Install to all agents even if not detected
skill-blast --force-agents

# Install specific skills by ID from GitHub (with sub-agent & multi-agent support)
skill-blast --github-install 1 41

# Install from GitHub to specific agents only
skill-blast --github-install 2 --agents claude-code opencode

# View installed skills from the local registry
skill-blast --status
```

---

## 📋 All 50 Skills

<details>
<summary><b>🎨 UI / Design (9 skills)</b></summary>

| # | Name | Repo | Description |
|---|------|------|-------------|
| 1 | `frontend-design` | anthropics/skills | Most popular skill — bans Inter + purple gradients, forces bold aesthetics |
| 21 | `canvas-design` | anthropics/skills | Beautiful visual art in PNG and PDF |
| 22 | `algorithmic-art` | anthropics/skills | Generative art with p5.js — flow fields, particle systems |
| 19 | `nothing-design` | jqueryscript/awesome-claude-code | Nothing Phone monochrome design language |
| 18 | `3d-motion-design` | freshtechbro/claudedesignskills | 27 plugins: Three.js, GSAP, React Three Fiber, Framer |
| 16 | `color-expert` | meodai/skill.color-expert | 286K words of color science, OKLCH/OKLAB, WCAG |
| 17 | `hand-drawn-diagrams` | muthuishere/hand-drawn-diagrams | Excalidraw diagrams, animated SVG output |
| 23 | `design-auditor` | BehiSecc/awesome-claude-skills | 17-rule audit, scores /100, bilingual EN/KR |
| 20 | `gpt-image-2` | glebis/claude-skills | Image model with reasoning, 14 style presets |

</details>

<details>
<summary><b>📱 Content / Social Media (10 skills)</b></summary>

| # | Name | Repo | Description |
|---|------|------|-------------|
| 2 | `social-media-os` | charlie947/social-media-skills | Full OS: 350K followers, 100M views/year system |
| 6 | `voice-builder` | charlie947/social-media-skills | Writes about-me.md + voice.md from interview |
| 7 | `reels-scripting` | charlie947/social-media-skills | Reverse-engineers outlier Reels via Apify + Gemini |
| 8 | `post-scorer` | charlie947/social-media-skills | Scores drafts against your real post history |
| 9 | `youtube-thumbnail` | charlie947/social-media-skills | Branded thumbnail prompts for Gemini |
| 10 | `hook-generator` | charlie947/social-media-skills | PAS/AIDA/BAB/STAR/SLAY frameworks |
| 14 | `tweetclaw` | Xquik-dev/tweetclaw | 40+ X/Twitter actions |
| 15 | `x-article-publisher` | wshuyi/x-article-publisher-skill | Publish long-form articles to X |
| 29 | `twitter-algorithm` | ComposioHQ/awesome-claude-skills | Rewrites tweets for real reach |
| 34 | `social-media-research` | skainguyen1412/social-media-research-skill | Reddit + X sentiment with receipts |

</details>

<details>
<summary><b>✍️ Writing / Research (7 skills)</b></summary>

| # | Name | Repo | Description |
|---|------|------|-------------|
| 11 | `humanizer` | blader/humanizer | Removes AI-writing tells, multi-pass editing |
| 13 | `beautiful-prose` | SHADOWPR0/beautiful_prose | Hemingway-style writing contract |
| 3 | `daydream` | glebis/claude-skills | Mines knowledge base for non-obvious connections |
| 31 | `deep-research` | 199-biotechnologies/claude-deep-research-skill | 8-phase pipeline, Brave+Serper+Exa+Firecrawl |
| 32 | `academic-research` | Imbad0202/academic-research-skills | Full research → write → review pipeline |
| 33 | `evidence-dialogue` | glebis/claude-skills | FULL/Socratic/TLDR/STEELMAN/DECISION modes |
| 12 | `anything-notebooklm` | joeseesun/anything-to-notebooklm | 15+ sources → podcasts, quizzes, mindmaps |

</details>

<details>
<summary><b>📈 Marketing (7 skills) · 🗂️ Product (3) · ⚙️ Engineering (8) · 🎬 Media (4) · 🏥 Health (2)</b></summary>

Run `skill-blast --list` for the full table in your terminal.

</details>

---

## 🗂️ How it works

```
skill-blast
    │
    ├── 1. Clone each unique GitHub repo → ~/.skill-blast/cache/
    │         (one clone per repo, shared across all agents)
    │
    ├── 2. Copy skill directory → ~/.skill-blast/skills/<name>/
    │         (sparse copy for subdirectory skills)
    │
    └── 3. Symlink → each agent's skills directory
              ~/.claude/skills/<name>     → ~/.skill-blast/skills/<name>
              ~/.opencode/skills/<name>   → ~/.skill-blast/skills/<name>
              ...
```

- **Efficient**: Each GitHub repo is cloned once, no matter how many skills use it
- **Non-destructive**: Existing skills are never overwritten
- **Cross-platform**: Uses symlinks on Linux/macOS, directory copies on Windows
- **Cached**: Re-running is instant for already-cloned repos

---

## 🔄 Updating skills

```bash
skill-blast --update
```

Pulls `git pull` on every cached repo and refreshes your skill store.

---

## 🛠️ Management commands

```bash
# Check version
skill-blast --version

# Uninstall all skills
skill-blast --uninstall

# Uninstall only Media skills
skill-blast --uninstall --only Media

# Health diagnostics — broken symlinks, cache status, git connectivity
skill-blast --check

# Show detailed metadata about a specific skill
skill-blast --info 1

# View all installed skills with agent and timestamp info
skill-blast --status

# Install a specific skill by ID from GitHub (auto-detects agents + sub-agents)
skill-blast --github-install 1
```

---

## ❓ Troubleshooting

<details>
<summary><b>Windows: "A required privilege is not held" / symlink error</b></summary>

Windows restricts symlink creation by default. skill-blast automatically falls
back to directory copies on Windows, but if you see this error:

1. **Run as Administrator** — right-click your terminal → *Run as admin*
2. **Or enable Developer Mode** — Settings → Update & Security → For Developers → Developer Mode
3. **Or do nothing** — skill-blast will use full copies instead of symlinks

</details>

<details>
<summary><b>macOS/Linux: "Permission denied" when creating symlinks</b></summary>

Your agent directory may be owned by root:

```bash
sudo chown -R $(whoami) ~/.claude ~/.opencode ~/.gemini
```

</details>

<details>
<summary><b>"git not found" error</b></summary>

Install git:
- **Windows**: https://git-scm.com/download/win
- **macOS**: `brew install git` or run `xcode-select --install`
- **Linux**: `sudo apt install git` / `sudo dnf install git`

</details>

<details>
<summary><b>A specific skill fails to clone</b></summary>

The upstream repo may have moved or been deleted:

```bash
# Check manually:
git clone https://github.com/owner/repo --depth=1

# Skip that skill:
skill-blast --skip <ID>
```

Open an issue with title `[broken] skill-name` so we can update the URL.

</details>

<details>
<summary><b>Broken symlinks after an update</b></summary>

```bash
# Diagnose:
skill-blast --check

# Repair — re-clones and re-links:
skill-blast --update
```

</details>

---

## 🤝 Contributing

PRs welcome! To add a new skill:

1. Add an entry to `skill_blast/skills.py`
2. Test with `skill-blast --dry-run --only YourCategory`
3. Open a PR

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

---

## 📄 License

MIT — see [LICENSE](LICENSE)

---

<div align="center">

Made with ❤️ for the AI developer community

[⭐ Star this repo](https://github.com/Venkatesh-6921/skill-blast) · [🐛 Report a bug](https://github.com/Venkatesh-6921/skill-blast/issues) · [💡 Request a skill](https://github.com/Venkatesh-6921/skill-blast/issues)

</div>
