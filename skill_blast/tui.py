from collections import defaultdict

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TabbedContent, TabPane, DataTable
from rich.text import Text

from .skills import ALL_SKILLS, CATEGORIES

class SkillBlastTUI(App):
    """Interactive TUI for browsing skill-blast skills."""

    TITLE = "skill-blast"
    SUB_TITLE = "50 Top AI Agent Skills"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("tab", "app.focus_next", "Next Focus"),
        ("shift+tab", "app.focus_previous", "Prev Focus"),
    ]

    CSS = """
    TabbedContent {
        height: 100%;
    }
    DataTable {
        height: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        
        import os
        filter_str = os.environ.get("SKILLBLAST_TUI_FILTER")
        filters = filter_str.split(",") if filter_str else []

        skills_by_category = defaultdict(list)
        for s in ALL_SKILLS:
            if filters and s.category not in filters:
                continue
            skills_by_category[s.category].append(s)
            
        categories = [c for c in CATEGORIES if c in skills_by_category]
        if not categories:
            categories = list(skills_by_category.keys())

        with TabbedContent():
            for category in categories:
                category_skills = skills_by_category[category]
                # Proper sanitization for TabPane ID: only alphanumeric, underscore, or hyphen
                import re
                tab_id = re.sub(r"[^a-zA-Z0-9_-]", "_", category).lower()
                
                with TabPane(category, id=tab_id):
                    table = DataTable(zebra_stripes=True)
                    table.add_columns("ID", "Name", "Repo", "Description")
                    for s in category_skills:
                        name_text = Text(s.name, style="bold")
                        repo_text = Text(s.repo, style="dim cyan")
                        table.add_row(str(s.id), name_text, repo_text, s.desc)
                    yield table

        yield Footer()
