"""
All 50 top AI agent skills with metadata.
Source: 50 Best Claude Code Skills (community-curated list).
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Skill:
    id: int
    name: str           # slug used as folder name
    repo: str           # GitHub owner/repo
    subpath: Optional[str]  # None = full repo; "path/to/dir" = sparse copy
    desc: str
    category: str
    tags: list[str]

    @property
    def repo_url(self) -> str:
        return f"https://github.com/{self.repo}"

    @property
    def clone_url(self) -> str:
        return f"https://github.com/{self.repo}.git"


CATEGORY_COLORS = {
    "UI/Design":   "cyan",
    "Content":     "magenta",
    "Writing":     "blue",
    "Research":    "yellow",
    "Marketing":   "green",
    "Product":     "bright_blue",
    "Engineering": "bright_red",
    "Media":       "bright_magenta",
    "Health":      "bright_green",
}

CATEGORY_ICONS = {
    "UI/Design":   "🎨",
    "Content":     "📱",
    "Writing":     "✍️",
    "Research":    "🔬",
    "Marketing":   "📈",
    "Product":     "🗂️",
    "Engineering": "⚙️",
    "Media":       "🎬",
    "Health":      "🏥",
}

ALL_SKILLS: list[Skill] = [

    # ── UI / Design ────────────────────────────────────────────────────────────
    Skill(1,  "frontend-design",     "anthropics/skills",                    "skills/frontend-design",
          "Most popular skill ever — bans Inter font + purple gradients, forces bold aesthetics",
          "UI/Design", ["ui", "design", "react", "css"]),

    Skill(21, "canvas-design",       "anthropics/skills",                    "skills/canvas-design",
          "Beautiful visual art in PNG and PDF with proper aesthetic principles",
          "UI/Design", ["design", "art", "pdf"]),

    Skill(22, "algorithmic-art",     "anthropics/skills",                    "skills/algorithmic-art",
          "Generative art with p5.js — seeded randomness, flow fields, particle systems",
          "UI/Design", ["art", "generative", "p5js"]),

    Skill(19, "nothing-design",      "dominikmartn/nothing-design-skill",    "nothing-design",
          "Generates UI in Nothing Phone's design language — monochrome, typographic, industrial",
          "UI/Design", ["ui", "design", "minimalist"]),

    Skill(18, "3d-motion-design",    "freshtechbro/claudedesignskills",      None,
          "27 plugins: Three.js, GSAP, React Three Fiber, Framer Motion, Babylon.js, A-Frame",
          "UI/Design", ["3d", "animation", "threejs", "gsap"]),

    Skill(16, "color-expert",        "meodai/skill.color-expert",            None,
          "286,000 words of color science — OKLCH/OKLAB, palette generation, WCAG contrast",
          "UI/Design", ["color", "design", "accessibility"]),

    Skill(17, "hand-drawn-diagrams", "muthuishere/hand-drawn-diagrams",      None,
          "Generates hand-drawn Excalidraw diagrams from a prompt — animated SVG, PNG export",
          "UI/Design", ["diagrams", "excalidraw", "svg"]),

    Skill(23, "design-auditor",      "Ashutos1997/claude-design-auditor-skill", None,
          "Audits designs against 17 professional rules: typography, WCAG, spacing — scores /100",
          "UI/Design", ["audit", "wcag", "typography"]),

    Skill(20, "gpt-image-2",         "glebis/claude-skills",                 "gpt-image-2",
          "First image model with built-in reasoning — 14 style presets, 8 platform presets",
          "UI/Design", ["image", "ai", "generation"]),

    # ── Content / Social Media ─────────────────────────────────────────────────
    Skill(2,  "social-media-os",     "charlie947/social-media-skills",       None,
          "The full system behind 350K followers and 100M views/year — 17 skills",
          "Content", ["social", "linkedin", "content"]),

    Skill(6,  "voice-builder",       "charlie947/social-media-skills",       "skills/voice-builder",
          "Interviews you, analyzes samples, writes about-me.md + voice.md — stops AI output",
          "Content", ["voice", "writing", "personal"]),

    Skill(7,  "reels-scripting",     "charlie947/social-media-skills",       "skills/reels-scripting",
          "Reverse-engineers an outlier Reel via Apify + Gemini 2.5 Flash — writes your script",
          "Content", ["reels", "instagram", "video"]),

    Skill(8,  "post-scorer",         "charlie947/social-media-skills",       "skills/post-scorer",
          "Pulls your post history via Apify and scores any draft against what performs for you",
          "Content", ["linkedin", "scoring", "analytics"]),

    Skill(9,  "youtube-thumbnail",   "charlie947/social-media-skills",       "skills/youtube-thumbnail",
          "Video title → branded YouTube thumbnail prompt for Gemini — 350K-follower CTR playbook",
          "Content", ["youtube", "thumbnail", "video"]),

    Skill(10, "hook-generator",      "charlie947/social-media-skills",       "skills/hook-generator",
          "Generates hooks across PAS, AIDA, BAB, STAR, SLAY — solves the 3-second scroll stop",
          "Content", ["hooks", "copywriting", "linkedin"]),

    Skill(14, "tweetclaw",           "Xquik-dev/tweetclaw",                  None,
          "40+ X/Twitter actions: post, extract, monitor, compose, schedule — way beyond basic",
          "Content", ["twitter", "x", "automation"]),

    Skill(15, "x-article-publisher", "wshuyi/x-article-publisher-skill",     None,
          "Publish full articles to X/Twitter directly from Claude Code — threading + formatting",
          "Content", ["twitter", "publishing", "longform"]),

    Skill(29, "twitter-algorithm",   "ComposioHQ/awesome-claude-skills",     "twitter-algorithm-optimizer",
          "Analyzes + rewrites tweets using Twitter's open-source algorithm — optimizes real reach",
          "Content", ["twitter", "algorithm", "reach"]),

    Skill(34, "social-media-research","skainguyen1412/social-media-research-skill", None,
          "Live public opinion + trends on Reddit and X — sentiment with receipts",
          "Content", ["research", "reddit", "twitter"]),

    # ── Writing / Research ─────────────────────────────────────────────────────
    Skill(11, "humanizer",           "blader/humanizer",                     None,
          "Removes AI-writing tells: em-dash overuse, throat-clearing openers, synonym cycling",
          "Writing", ["writing", "editing", "humanize"]),

    Skill(13, "beautiful-prose",     "SHADOWPR0/beautiful_prose",            None,
          "Hard-edged writing style contract — closer to Hemingway than ChatGPT, zero fluff",
          "Writing", ["writing", "style", "prose"]),

    Skill(3,  "daydream",            "glebis/claude-skills",                 "daydream",
          "Mines your knowledge base for non-obvious connections while you sleep — ~40¢/run",
          "Research", ["knowledge", "connections", "background"]),

    Skill(31, "deep-research",       "199-biotechnologies/claude-deep-research-skill", None,
          "8-phase pipeline: Brave+Serper+Exa+Jina+Firecrawl — beats OpenAI Deep Research",
          "Research", ["research", "search", "sources"]),

    Skill(32, "academic-research",   "Imbad0202/academic-research-skills",   None,
          "Full pipeline: research → write → review → revise → finalize — AI pattern checker",
          "Research", ["academic", "research", "writing"]),

    Skill(33, "evidence-dialogue",   "glebis/claude-skills",                 "balanced",
          "Replaces sycophancy — 5 modes: FULL, Socratic, TLDR, STEELMAN, DECISION",
          "Research", ["critical", "thinking", "debate"]),

    Skill(12, "anything-notebooklm", "joeseesun/anything-to-notebooklm",     None,
          "Converts 15+ sources (YouTube, PDFs, web) into podcasts, presentations, quizzes",
          "Research", ["notebooklm", "podcast", "research"]),

    # ── Marketing ──────────────────────────────────────────────────────────────
    Skill(26, "marketing-module",    "alirezarezvani/claude-skills",         "marketing-skill",
          "43 marketing skills in 7 pods: Content, SEO, CRO, Channels, Growth, Intelligence, Sales",
          "Marketing", ["marketing", "seo", "cro"]),

    Skill(27, "marketing-skills-ch", "coreyhaines31/marketingskills",        None,
          "CRO, copywriting, SEO, analytics, growth engineering, ad creative, Reels/TikTok/Shorts",
          "Marketing", ["marketing", "cro", "copywriting"]),

    Skill(28, "email-bible",         "CosmoBlk/email-marketing-bible",       None,
          "55,000-word email marketing guide — subject lines, lifecycle flows, win-back sequences",
          "Marketing", ["email", "marketing", "automation"]),

    Skill(30, "competitive-ads",     "ComposioHQ/awesome-claude-skills",     "competitive-ads-extractor",
          "Pulls competitors' ads from ad libraries — analyzes messaging + creative patterns",
          "Marketing", ["ads", "competitive", "analysis"]),

    Skill(24, "kim-barrett-dr",      "VoltAgent/awesome-agent-skills",       None,
          "Direct-response copy: avatar extraction, Schwartz mapper, headline matrix, objection crusher",
          "Marketing", ["copywriting", "direct-response", "ads"]),

    Skill(44, "geo-seo",             "AgriciDaniel/claude-seo",              None,
          "GEO-first SEO: AI search optimization, citability scoring, AI crawler analysis, PDF reports",
          "Marketing", ["seo", "geo", "ai-search"]),

    Skill(25, "wondelai-ux-growth",  "wondelai/skills",                      None,
          "25 skills grounded in Norman, Cialdini, Ries, Hormozi — UX, marketing, growth",
          "Marketing", ["ux", "growth", "frameworks"]),

    # ── Product / PM ───────────────────────────────────────────────────────────
    Skill(35, "pm-skills",           "phuryn/pm-skills",                     None,
          "100+ PM skills: Discovery, Lean Canvas, JTBD, OKRs, PRDs, pricing, slash commands",
          "Product", ["pm", "product", "jtbd"]),

    Skill(36, "jtbd-interview",      "glebis/claude-skills",                 "skill-studio",
          "Live Jobs-To-Be-Done interview — converts customer interviews into briefs + copy",
          "Product", ["jtbd", "interviews", "product"]),

    Skill(37, "ai-transformation",   "glebis/claude-skills",                 "context-builder",
          "Express (15-20 min) or Deep Dive (60-90 min) AI consulting interview with BCG/Ng frameworks",
          "Product", ["consulting", "ai", "strategy"]),

    # ── Engineering ────────────────────────────────────────────────────────────
    Skill(41, "superpowers",         "obra/superpowers",                     None,
          "The most popular community skill — 14 bundled skills, 725K+ installs",
          "Engineering", ["coding", "engineering", "senior"]),

    Skill(42, "repomix",             "yamadashy/repomix",                    None,
          "Packs your entire repo into one AI-friendly file — fastest codebase feeding",
          "Engineering", ["repo", "context", "tools"]),

    Skill(43, "antfu-skills",        "antfu/skills",                         None,
          "Production-grade skills curated by Anthony Fu — Vue/Vite core team member",
          "Engineering", ["vue", "vite", "production"]),

    Skill(5,  "autoresearch",        "uditgoenka/autoresearch",              None,
          "Karpathy-inspired self-improvement engine — 9 modes: code-pr, deployment, marketing…",
          "Engineering", ["research", "automation", "ai"]),

    Skill(45, "dev-browser",         "SawyerHood/dev-browser",               None,
          "Gives your agent a web browser — end-to-end QA, research, automation",
          "Engineering", ["browser", "automation", "qa"]),

    Skill(46, "vexor-search",        "scarletkc/vexor",                      None,
          "Vector-powered semantic file search — local, private, fast",
          "Engineering", ["search", "vector", "semantic"]),

    Skill(47, "skill-seekers",       "yusufkaraaslan/Skill_Seekers",         None,
          "Convert any docs site, GitHub repo, or PDF into a Claude skill in minutes",
          "Engineering", ["skills", "converter", "docs"]),

    Skill(48, "web-scraper",         "yfe404/web-scraper",                   None,
          "Intelligent scraper: curl → quality gate → stealth browser → API sniff → validate",
          "Engineering", ["scraping", "web", "data"]),

    # ── Media / Creative ────────────────────────────────────────────────────────
    Skill(4,  "remotion",            "remotion-dev/skills",                  "skills/remotion",
          "Make videos programmatically in React — 30+ rules: 3D, TikTok captions, FFmpeg",
          "Media", ["video", "remotion", "react"]),

    Skill(38, "ai-video-toolkit",    "digitalsamba/claude-code-video-toolkit", None,
          "End-to-end AI-native video pipeline: script → voiceover → Remotion → MP4",
          "Media", ["video", "ai", "voiceover"]),

    Skill(39, "ai-music-production", "bitwize-music-studio/claude-ai-music-skills", None,
          "Full lifecycle: lyrics → Suno prompts → per-stem mixing → mastering → distribution",
          "Media", ["music", "suno", "production"]),

    Skill(40, "generative-media",    "SamurAIGPT/Generative-Media-Skills",   None,
          "Multi-modal generative media: image, video, audio across AI providers",
          "Media", ["generative", "multimodal", "media"]),

    # ── Health ──────────────────────────────────────────────────────────────────
    Skill(49, "personal-health",     "Aperivue/medsci-skills",               None,
          "Analyzes medical reports, tracks health metrics, personalized wellness suggestions",
          "Health", ["health", "medical", "wellness"]),

    Skill(50, "dna-analysis",        "shmlkv/dna-claude-analysis",           None,
          "Personal genome analysis from 23andMe/Ancestry — 17 categories including pharmacogenomics",
          "Health", ["dna", "genome", "ancestry"]),
]

# Lookup helpers
SKILLS_BY_ID: dict[int, Skill] = {s.id: s for s in ALL_SKILLS}
CATEGORIES: list[str] = sorted(set(s.category for s in ALL_SKILLS))
