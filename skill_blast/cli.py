"""
skill-blast CLI — works for both developers (flags) and non-developers (wizard).
"""

from __future__ import annotations

import argparse
import concurrent.futures
import sys
import platform
from pathlib import Path

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.progress import (BarColumn, MofNCompleteColumn, Progress,
                           SpinnerColumn, TaskProgressColumn, TextColumn,
                           TimeElapsedColumn)
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

from . import __version__
from .agents import AGENTS, detect_agents
from .installer import (check_git, install_skill, uninstall_skill,
                        health_check, batch_update_repos, CACHE_DIR, STORE_DIR)
from .skills import (ALL_SKILLS, CATEGORIES, CATEGORY_COLORS,
                     CATEGORY_ICONS, Skill, SKILLS_BY_ID)

# Fix Unicode output on Windows (box-drawing chars + emoji in BANNER/agents).
# Without this, CP1252/CP437 terminals raise UnicodeEncodeError on first print.
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass  # reconfigure not available on some legacy Python builds

console = Console()


# ── UI helpers ─────────────────────────────────────────────────────────────────

BANNER = """[bold cyan]
  ███████╗██╗  ██╗██╗██╗     ██╗       ██████╗ ██╗      █████╗ ███████╗████████╗
  ██╔════╝██║ ██╔╝██║██║     ██║       ██╔══██╗██║     ██╔══██╗██╔════╝╚══██╔══╝
  ███████╗█████╔╝ ██║██║     ██║ █████╗██████╔╝██║     ███████║███████╗   ██║
  ╚════██║██╔═██╗ ██║██║     ██║ ╚════╝██╔══██╗██║     ██╔══██║╚════██║   ██║
  ███████║██║  ██╗██║███████╗███████╗  ██████╔╝███████╗██║  ██║███████║   ██║
  ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝
[/bold cyan]"""


def print_banner() -> None:
    console.print(BANNER)
    console.print(
        "[dim]  One-click installer for 50 top AI agent skills[/]"
        "  ·  [cyan]github.com/Venkatesh-6921/skill-blast[/]\n"
    )


def _cat_display(cat: str) -> str:
    icon = CATEGORY_ICONS.get(cat, "•")
    color = CATEGORY_COLORS.get(cat, "white")
    return f"[{color}]{icon} {cat}[/]"


# ── Wizard (non-developer mode) ────────────────────────────────────────────────

def run_wizard() -> tuple[list[str], list[str], bool]:
    """
    Interactive step-by-step wizard.
    Returns: (agent_keys, categories, dry_run)
    """
    console.print(Panel(
        "👋  [bold]Welcome![/]  This wizard will walk you through installing AI skills.\n"
        "    No coding knowledge needed. Just answer a few questions.\n\n"
        "    [dim]Press Ctrl+C at any time to cancel.[/]",
        border_style="cyan",
    ))
    console.print()

    # ── Step 1: Agents ─────────────────────────────────────────────────────────
    detected = detect_agents()

    agent_choices = []
    for key, agent in AGENTS.items():
        is_detected = key in detected
        mark = " (Detected)" if is_detected else ""
        agent_choices.append(questionary.Choice(
            title=f"{agent['icon']} {agent['name']}{mark}",
            value=key,
            checked=is_detected
        ))
        
    chosen_agents = questionary.checkbox(
        "Which AI agents do you want to install skills for?",
        choices=agent_choices,
        instruction="(Use Space to select, Enter to confirm)"
    ).ask()

    # If the user cancels (Ctrl+C), it returns None
    if chosen_agents is None:
        sys.exit(0)
    
    if not chosen_agents:
        chosen_agents = list(detected.keys()) or ["claude-code"]

    console.print()
    console.print("[green]✓[/] Will install to: " + ", ".join(AGENTS[k]["name"] for k in chosen_agents))
    console.print()

    # ── Step 2: Categories ─────────────────────────────────────────────────────
    cats = sorted(CATEGORIES)
    cat_choices = []
    for cat in cats:
        count = sum(1 for s in ALL_SKILLS if s.category == cat)
        icon = CATEGORY_ICONS.get(cat, "•")
        cat_choices.append(questionary.Choice(
            title=f"{icon} {cat} ({count} skills)",
            value=cat,
            checked=True
        ))

    chosen_cats = questionary.checkbox(
        "Which skill categories do you want?",
        choices=cat_choices,
        instruction="(Use Space to select, Enter to confirm)"
    ).ask()

    if chosen_cats is None:
        sys.exit(0)
    
    if not chosen_cats:
        chosen_cats = cats

    skill_count = sum(1 for s in ALL_SKILLS if s.category in chosen_cats)
    console.print()
    console.print(f"[green]✓[/] Will install [bold]{skill_count}[/] skills from: " + ", ".join(chosen_cats))
    console.print()

    # ── Step 3: Confirm ────────────────────────────────────────────────────────
    console.print("[bold]Step 3 of 3[/] — [cyan]Ready to install?[/]\n")
    console.print(f"  • [bold]{skill_count}[/] skills")
    console.print(f"  • Target agents: [bold]{', '.join(AGENTS[k]['name'] for k in chosen_agents)}[/]")
    console.print(f"  • Cache location: [dim]{CACHE_DIR}[/]")
    console.print()

    dry = Confirm.ask("  Preview only (dry run, no files written)?", default=False)
    console.print()

    if not dry:
        go = Confirm.ask("  [bold green]Start installation?[/]", default=True)
        if not go:
            console.print("[yellow]Cancelled.[/]")
            sys.exit(0)

    return chosen_agents, chosen_cats, dry


# ── List all skills ─────────────────────────────────────────────────────────────

def cmd_list(category_filter: list[str] | None = None) -> None:
    skills = ALL_SKILLS if not category_filter else [s for s in ALL_SKILLS if s.category in category_filter]
    skills = sorted(skills, key=lambda x: (x.category, x.id))

    table = Table(
        title=f"[bold]skill-blast — {len(skills)} Skills[/]",
        border_style="bright_black",
        show_lines=False,
        expand=True,
    )
    table.add_column("ID", style="dim", width=4, no_wrap=True)
    table.add_column("Category", width=14)
    table.add_column("Name", width=24, style="bold")
    table.add_column("Repo", style="dim cyan", width=34)
    table.add_column("Description")

    prev_cat = ""
    for s in skills:
        cat_display = ""
        if s.category != prev_cat:
            cat_display = _cat_display(s.category)
            prev_cat = s.category
        table.add_row(str(s.id), cat_display, s.name, s.repo, s.desc)

    console.print(table)
    console.print(f"\n[dim]Total: {len(skills)} skills across {len(CATEGORIES)} categories[/]")


# ── Skill Info ──────────────────────────────────────────────────────────────────

def cmd_info(skill_id: int) -> None:
    skill = SKILLS_BY_ID.get(skill_id)
    if not skill:
        console.print(f"[bold red]Error:[/] Skill ID {skill_id} not found.")
        sys.exit(1)

    cat_display = _cat_display(skill.category)

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="bold cyan", width=12)
    table.add_column("Value")

    table.add_row("ID", str(skill.id))
    table.add_row("Name", f"[bold]{skill.name}[/]")
    table.add_row("Category", cat_display)
    table.add_row("Description", skill.desc)
    table.add_row("Repository", f"[link={skill.repo_url}]{skill.repo}[/link]")
    if skill.subpath:
        table.add_row("Subpath", skill.subpath)
    table.add_row("Tags", ", ".join(skill.tags) if skill.tags else "None")

    console.print(Panel(table, title=f"Skill Info: {skill.name}", border_style="cyan", expand=False))


# ── Uninstall ───────────────────────────────────────────────────────────────────

def run_uninstall(
    skills: list[Skill],
    agent_dirs: list[Path],
) -> list[dict]:
    results: list[dict] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description:<40}"),
        BarColumn(),
        MofNCompleteColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    ) as progress:
        task = progress.add_task("[red]Uninstalling…", total=len(skills))

        def _uninstall_one(skill: Skill) -> dict:
            return uninstall_skill(skill, agent_dirs)

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            future_to_skill = {
                executor.submit(_uninstall_one, s): s for s in skills
            }
            for future in concurrent.futures.as_completed(future_to_skill):
                skill = future_to_skill[future]
                color = CATEGORY_COLORS.get(skill.category, "white")
                progress.update(
                    task,
                    description=(
                        f"[{color}]{CATEGORY_ICONS.get(skill.category, '•')} {skill.category:10}[/] "
                        f"[bold]{skill.name}[/]"
                    ),
                )
                try:
                    result = future.result()
                except Exception as exc:
                    result = {"skill": skill, "ok": False, "removed": [], "not_found": [], "error": str(exc)}

                results.append(result)

                if result["ok"]:
                    removed = ", ".join(result["removed"])
                    console.log(
                        f"  [green]✓[/] [bold]{skill.name}[/] removed"
                        + (f"  ← {removed}" if removed else " (not installed)")
                    )
                else:
                    console.log(f"  [red]✗[/] [bold]{skill.name}[/]  [red]{result['error']}[/]")

                progress.advance(task)

    return results


def print_uninstall_summary(results: list[dict]) -> None:
    ok = [r for r in results if r["ok"]]
    removed_count = sum(len(r["removed"]) for r in ok)
    failed = [r for r in results if not r["ok"]]

    console.print()
    console.print(Panel(
        f"[bold green]✓ {len(ok)} processed[/]    "
        f"[dim]{removed_count} links removed[/]    "
        + (f"[bold red]✗ {len(failed)} failed[/]" if failed else "[green]0 failures[/]"),
        title="[bold]Uninstall Summary[/]",
        border_style="bright_black",
    ))


# ── Health check ────────────────────────────────────────────────────────────────

def cmd_check() -> None:
    """Run diagnostics on the skill-blast installation."""
    agent_dirs = [a["skills_dir"] for a in AGENTS.values()]
    report = health_check(agent_dirs)

    console.print(Panel(
        "[bold]skill-blast health check[/]",
        border_style="cyan",
    ))

    # Git
    git_icon = "[green]✓[/]" if report["git_ok"] else "[red]✗[/]"
    console.print(f"  {git_icon} git: {report['git_msg']}")

    # Cache
    cache_icon = "[green]✓[/]" if report["cache_exists"] else "[yellow]○[/]"
    console.print(f"  {cache_icon} Cache: {CACHE_DIR}  ({report['cached_repos']} repos)")

    # Store
    store_icon = "[green]✓[/]" if report["store_exists"] else "[yellow]○[/]"
    console.print(f"  {store_icon} Store: {STORE_DIR}  ({report['stored_skills']} skills)")

    # Links
    console.print(f"  [green]✓[/] Healthy links: {report['healthy_links']}")

    if report["broken_links"]:
        console.print(f"  [red]✗[/] Broken symlinks: {len(report['broken_links'])}")
        for link in report["broken_links"]:
            console.print(f"    [red]→[/] {link}")
        console.print()
        console.print("  [dim]Tip: run [/][bold]skill-blast --update[/][dim] to repair broken links.[/]")
    else:
        console.print(f"  [green]✓[/] No broken symlinks")

    console.print()


# ── Progress install ────────────────────────────────────────────────────────────

def run_install(
    skills: list[Skill],
    agent_dirs: list[Path],
    dry_run: bool,
    update: bool,
) -> list[dict]:
    results: list[dict] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description:<40}"),
        BarColumn(),
        MofNCompleteColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    ) as progress:
        task = progress.add_task("[cyan]Installing…", total=len(skills))

        def _install_one(skill: Skill) -> dict:
            return install_skill(skill, agent_dirs, dry_run=dry_run, update=update)

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            future_to_skill = {
                executor.submit(_install_one, s): s for s in skills
            }
            for future in concurrent.futures.as_completed(future_to_skill):
                skill = future_to_skill[future]
                color = CATEGORY_COLORS.get(skill.category, "white")
                progress.update(
                    task,
                    description=(
                        f"[{color}]{CATEGORY_ICONS.get(skill.category, '•')} {skill.category:10}[/] "
                        f"[bold]{skill.name}[/]"
                    ),
                )
                try:
                    result = future.result()
                except Exception as exc:
                    result = {"skill": skill, "ok": False, "repo_msg": "", "linked": [], "already": [], "error": str(exc)}

                results.append(result)

                if result["ok"]:
                    msg = result["repo_msg"]
                    linked = ", ".join(result["linked"])
                    console.log(
                        f"  [green]✓[/] [bold]{skill.name}[/] "
                        f"[dim]({msg})[/]"
                        + (f"  → {linked}" if linked else "")
                    )
                else:
                    console.log(f"  [red]✗[/] [bold]{skill.name}[/]  [red]{result['error']}[/]")

                progress.advance(task)

    return results


# ── Summary ─────────────────────────────────────────────────────────────────────

def print_summary(results: list[dict], agent_names: list[str]) -> None:
    ok = [r for r in results if r["ok"]]
    failed = [r for r in results if not r["ok"]]
    already = sum(len(r["already"]) for r in ok)

    console.print()
    console.print(Panel(
        f"[bold green]✓ {len(ok)} installed[/]    "
        f"[dim]{already} already existed[/]    "
        + (f"[bold red]✗ {len(failed)} failed[/]" if failed else "[green]0 failures[/]"),
        title="[bold]Installation Summary[/]",
        border_style="bright_black",
    ))

    if failed:
        table = Table(title="[red]Failed Skills[/]", border_style="red", show_lines=False)
        table.add_column("ID", width=4, style="dim")
        table.add_column("Name", style="bold red")
        table.add_column("Reason")
        for r in failed:
            table.add_row(str(r["skill"].id), r["skill"].name, r["error"] or "?")
        console.print(table)

    console.print()
    console.print(Panel(
        f"[bold]Cache:[/]  {CACHE_DIR}\n"
        f"[bold]Store:[/]  {STORE_DIR}\n\n"
        "[bold]Next steps by agent:[/]\n"
        + "\n".join(
            f"  {AGENTS[k]['icon']} [cyan]{AGENTS[k]['name']:15}[/] {AGENTS[k]['note']}"
            for k in agent_names
            if k in AGENTS
        )
        + "\n\n[dim]Run [/][bold]skill-blast --update[/][dim] anytime to pull the latest skill versions.[/]",
        title="[bold green]Done! 🎉[/]",
        border_style="green",
    ))


# ── Entry point ─────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="skill-blast",
        description="One-click installer for 50 top AI agent skills",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  skill-blast                          # interactive wizard (recommended for beginners)
  skill-blast --all                    # install everything, auto-detect agents
  skill-blast --agents claude-code opencode
  skill-blast --only Engineering "UI/Design"
  skill-blast --skip 41 49 50
  skill-blast --update                 # pull latest for cached repos
  skill-blast --dry-run                # preview without writing files
  skill-blast --list                   # show all 50 skills
  skill-blast --list --only Marketing  # filter list by category
  skill-blast --uninstall              # remove all installed skills
  skill-blast --uninstall --only Media # remove only Media skills
  skill-blast --check                  # run health diagnostics
        """,
    )
    parser.add_argument("--version", action="version",
                        version=f"%(prog)s {__version__}")
    parser.add_argument("--agents", nargs="+", choices=list(AGENTS), metavar="AGENT",
                        help="Target specific agents (default: auto-detect)")
    parser.add_argument("--all", action="store_true",
                        help="Install all skills to all detected agents")
    parser.add_argument("--only", nargs="+", metavar="CATEGORY",
                        help=f"Install only these categories: {', '.join(CATEGORIES)}")
    parser.add_argument("--skip", nargs="+", type=int, metavar="ID",
                        help="Skill IDs to skip")
    parser.add_argument("--update", action="store_true",
                        help="Pull latest for already-cached repos")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without writing any files")
    parser.add_argument("--list", action="store_true",
                        help="List all skills and exit")
    parser.add_argument("--uninstall", action="store_true",
                        help="Remove installed skills from agent directories")
    parser.add_argument("--info", type=int, metavar="ID",
                        help="Show detailed info about a specific skill")
    parser.add_argument("--check", action="store_true",
                        help="Run health diagnostics on your skill-blast installation")
    parser.add_argument("--force-agents", action="store_true",
                        help="Install to ALL agents even if not detected")
    parser.add_argument("--no-wizard", action="store_true",
                        help="Skip interactive wizard; use flags only")
    parser.add_argument("--add", metavar="GITHUB_REPO",
                        help="Add a custom skill from a GitHub repository (e.g. username/repo)")
    parser.add_argument("--category", metavar="CATEGORY", default="Custom",
                        help="Category for the custom skill (default: Custom)")
    parser.add_argument("--desc", metavar="DESCRIPTION", default="Custom user-added skill",
                        help="Description for the custom skill")
    args = parser.parse_args()

    # ── List only ──────────────────────────────────────────────────────────────
    if args.list:
        print_banner()
        cmd_list(category_filter=args.only)
        return

    # ── Add custom skill ───────────────────────────────────────────────────────
    if args.add:
        from .skills import add_custom_skill
        print_banner()
        console.print(f"[bold cyan]Adding custom skill:[/] {args.add}")
        skill = add_custom_skill(args.add, args.category, args.desc)
        console.print(f"[green]✓ Successfully added {skill.name} to local database.[/]")
        console.print("It will be included in future installations.")
        return

    # ── Info only ──────────────────────────────────────────────────────────────
    if args.info is not None:
        print_banner()
        cmd_info(args.info)
        return

    # ── Health check ──────────────────────────────────────────────────────────
    if args.check:
        print_banner()
        cmd_check()
        return

    print_banner()

    # ── Git check ──────────────────────────────────────────────────────────────
    git_ok, git_msg = check_git()
    if not git_ok:
        console.print(Panel(
            "[bold red]git is not installed or not in PATH.[/]\n\n"
            "Please install git first:\n"
            "  • [cyan]Windows[/]:  https://git-scm.com/download/win\n"
            "  • [cyan]macOS[/]:    brew install git  (or via Xcode tools)\n"
            "  • [cyan]Linux[/]:    sudo apt install git   /   sudo dnf install git\n\n"
            "Then re-run skill-blast.",
            title="[red]Missing dependency[/]",
            border_style="red",
        ))
        sys.exit(1)

    # ── Decide: wizard or flags ────────────────────────────────────────────────
    use_wizard = not (args.all or args.agents or args.only or args.skip
                      or args.dry_run or args.no_wizard or args.uninstall or args.add)

    if use_wizard:
        # Non-developer path
        chosen_agent_keys, chosen_cats, dry_run = run_wizard()
    else:
        # Developer / flag path
        dry_run = args.dry_run

        if args.agents:
            chosen_agent_keys = args.agents
        elif args.force_agents:
            chosen_agent_keys = list(AGENTS.keys())
        else:
            detected = detect_agents()
            chosen_agent_keys = list(detected.keys()) or ["claude-code"]
            if chosen_agent_keys == ["claude-code"]:
                console.print("[yellow]No agents detected — defaulting to Claude Code.[/]\n")

        chosen_cats = args.only if args.only else CATEGORIES

    # ── Filter skills ──────────────────────────────────────────────────────────
    skills = [s for s in ALL_SKILLS if s.category in chosen_cats]
    if args.skip:
        skills = [s for s in skills if s.id not in args.skip]

    agent_dirs = [AGENTS[k]["skills_dir"] for k in chosen_agent_keys]

    # ── Status line ────────────────────────────────────────────────────────────
    console.print(f"[bold]Agents:[/] {', '.join(AGENTS[k]['name'] for k in chosen_agent_keys)}")
    console.print(f"[bold]Skills:[/] {len(skills)}  "
                  f"[dim]({', '.join(chosen_cats)})[/]")
    if dry_run:
        console.print("[bold yellow]DRY RUN — no files will be written[/]")
    console.print()

    # ── Uninstall path ─────────────────────────────────────────────────────────
    if args.uninstall:
        console.print(f"[bold red]Uninstalling {len(skills)} skills…[/]\n")
        results = run_uninstall(skills, agent_dirs)
        print_uninstall_summary(results)
        return

    # ── Concurrent repo update ─────────────────────────────────────────────────
    if args.update and not dry_run:
        unique_repos = sorted(set(s.repo for s in skills))
        console.print(f"[cyan]Updating {len(unique_repos)} repos concurrently (4 threads)…[/]\n")
        repo_results = batch_update_repos(unique_repos, max_workers=4)
        ok_count = sum(1 for ok, _ in repo_results.values() if ok)
        fail_count = len(repo_results) - ok_count
        console.print(
            f"  [green]✓ {ok_count} repos updated[/]"
            + (f"  [red]✗ {fail_count} failed[/]" if fail_count else "")
            + "\n"
        )

    # ── Install ────────────────────────────────────────────────────────────────
    results = run_install(skills, agent_dirs, dry_run=dry_run, update=args.update)

    # ── Summary ────────────────────────────────────────────────────────────────
    print_summary(results, chosen_agent_keys)


if __name__ == "__main__":
    main()
