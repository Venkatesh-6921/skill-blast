import os
import re
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
    ]

    CSS = """
    Screen {
        layout: vertical;
    }
    TabbedContent {
        height: 1fr;
    }
    ContentSwitcher {
        height: 1fr;
    }
    TabPane {
        height: 1fr;
        padding: 0;
    }
    DataTable {
        height: 1fr;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        filter_str = os.environ.get("SKILLBLAST_TUI_FILTER")
        self._filters = filter_str.split(",") if filter_str else []

        self._skills_by_cat: dict[str, list] = defaultdict(list)
        for s in ALL_SKILLS:
            if self._filters and s.category not in self._filters:
                continue
            self._skills_by_cat[s.category].append(s)

        self._categories = [c for c in CATEGORIES if c in self._skills_by_cat]
        if not self._categories and self._skills_by_cat:
            self._categories = sorted(self._skills_by_cat.keys())

    def _safe_id(self, category: str) -> str:
        """Generate a valid CSS/Textual widget identifier from a category name."""
        return re.sub(r"[^a-zA-Z0-9_-]", "_", category).lower()

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            for cat in self._categories:
                safe = self._safe_id(cat)
                with TabPane(cat, id=f"pane-{safe}"):
                    yield DataTable(id=f"dt-{safe}", zebra_stripes=True)
        yield Footer()

    def on_mount(self) -> None:
        """Populate every DataTable after the widget tree is fully mounted."""
        for cat in self._categories:
            safe = self._safe_id(cat)
            table = self.query_one(f"#dt-{safe}", DataTable)
            table.cursor_type = "row"
            table.add_columns("ID", "Name", "Repo", "Description")
            for s in self._skills_by_cat[cat]:
                table.add_row(
                    str(s.id),
                    Text(s.name, style="bold cyan"),
                    Text(s.repo, style="dim"),
                    s.desc,
                )

