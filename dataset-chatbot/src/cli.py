#!/usr/bin/env python3
"""Textual CLI interface for dataset chatbot."""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import (Footer, Header, Input, Label, ListItem, ListView,
                             Static, TabbedContent, TabPane, TextArea)

from src.datasource import DataSource, load_datasources
from src.processor import DuckDBProcessor, DummyProcessor


class DatasetListItem(ListItem):
    """A list item representing a CSV dataset."""

    DEFAULT_CSS = """
    DatasetListItem {
        height: auto;
        padding: 1;
    }
    DatasetListItem > Label {
        width: 100%;
    }
    """

    def __init__(self, datasource: DataSource) -> None:
        super().__init__()
        self.datasource = datasource

    def compose(self) -> ComposeResult:
        ds = self.datasource
        yield Label(f"{ds.name} ({ds.row_count} rows)")


class ChatMessage(Static):
    """A chat message widget."""

    DEFAULT_CSS = """
    ChatMessage {
        padding: 1;
        margin-bottom: 1;
    }
    ChatMessage.question {
        background: $primary-darken-2;
        border-left: thick $primary;
    }
    ChatMessage.answer {
        background: $surface;
        border-left: thick $success;
    }
    """

    def __init__(self, content: str, is_question: bool = True) -> None:
        super().__init__(content)
        self.add_class("question" if is_question else "answer")


class DatasetDescriptionTab(Horizontal):
    """Tab for describing datasets."""

    DEFAULT_CSS = """
    DatasetDescriptionTab {
        height: 100%;
        width: 100%;
    }

    #dataset-sidebar {
        width: 30;
        min-width: 25;
        height: 100%;
        border-right: solid $primary;
    }

    #dataset-sidebar-title {
        text-style: bold;
        padding: 1;
        border-bottom: solid $primary-darken-2;
        height: auto;
    }

    #dataset-list {
        height: 1fr;
    }

    #no-datasets {
        color: $text-muted;
        padding: 1;
    }

    #description-panel {
        width: 1fr;
        height: 100%;
        padding: 1;
    }

    #description-title {
        text-style: bold;
        padding-bottom: 1;
        height: auto;
    }

    #description-area {
        height: 1fr;
    }

    #no-selection {
        color: $text-muted;
        padding: 2;
    }
    """

    def __init__(self, datasources: list[DataSource]) -> None:
        super().__init__()
        self.datasources = datasources
        self.current_datasource: DataSource | None = None

    def compose(self) -> ComposeResult:
        with Vertical(id="dataset-sidebar"):
            yield Static("CSV Datasets", id="dataset-sidebar-title")
            if self.datasources:
                yield ListView(
                    *[DatasetListItem(ds) for ds in self.datasources],
                    id="dataset-list",
                )
            else:
                yield Static("No datasets loaded", id="no-datasets")

        with Vertical(id="description-panel"):
            yield Static("Dataset Description", id="description-title")
            if self.datasources:
                yield TextArea(id="description-area", show_line_numbers=True)
            else:
                yield Static("No CSV files loaded", id="no-selection")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle dataset selection from the list."""
        if isinstance(event.item, DatasetListItem):
            self._save_current_description()
            self.current_datasource = event.item.datasource
            self._load_description(event.item.datasource)

    def _save_current_description(self) -> None:
        """Save the current description before switching."""
        if self.current_datasource is not None:
            try:
                text_area = self.query_one("#description-area", TextArea)
                self.current_datasource.description = text_area.text
            except Exception:
                pass

    def _load_description(self, datasource: DataSource) -> None:
        """Load or generate description for a dataset."""
        try:
            text_area = self.query_one("#description-area", TextArea)
        except Exception:
            return

        if datasource.description:
            text_area.text = datasource.description
        else:
            description = datasource.generate_description_template()
            datasource.description = description
            text_area.text = description

    def on_mount(self) -> None:
        """Select first dataset on mount."""
        if self.datasources:
            self.current_datasource = self.datasources[0]
            self._load_description(self.datasources[0])


class ChatTab(Container):
    """Tab for chatting with the data."""

    DEFAULT_CSS = """
    ChatTab {
        layout: vertical;
        height: 100%;
    }

    #chat-history {
        height: 1fr;
        border-bottom: solid $primary;
        padding: 1;
    }

    #chat-input-container {
        height: auto;
        padding: 1;
    }

    #chat-input {
        margin-top: 1;
    }

    #chat-prompt {
        color: $text-muted;
    }
    """

    def __init__(
        self, datasources: list[DataSource], processor: DummyProcessor
    ) -> None:
        super().__init__()
        self.datasources = datasources
        self.processor = processor

    def compose(self) -> ComposeResult:
        yield VerticalScroll(id="chat-history")
        with Vertical(id="chat-input-container"):
            yield Static("Ask a question about your data:", id="chat-prompt")
            yield Input(placeholder="Type your question here...", id="chat-input")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle question submission."""
        question = event.value.strip()
        if not question:
            return

        event.input.value = ""

        history = self.query_one("#chat-history", VerticalScroll)

        history.mount(ChatMessage(f"> {question}", is_question=True))

        response = self.processor.process(question)
        history.mount(ChatMessage(response, is_question=False))

        history.scroll_end(animate=False)


class DatasetChatbotApp(App):
    """Main Textual application for the dataset chatbot."""

    TITLE = "Dataset Chatbot"
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
        height: 100%;
        padding: 0;
    }

    DatasetDescriptionTab {
        height: 100%;
    }

    ChatTab {
        height: 100%;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("d", "switch_tab('dataset')", "Datasets"),
        Binding("c", "switch_tab('chat')", "Chat"),
    ]

    def __init__(self, datasources: list[DataSource]) -> None:
        super().__init__()
        self.datasources = datasources
        self.processor = DuckDBProcessor(self.datasources)

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            with TabPane("Dataset Description", id="dataset"):
                yield DatasetDescriptionTab(self.datasources)
            with TabPane("Chat with Data", id="chat"):
                yield ChatTab(self.datasources, self.processor)
        yield Footer()

    def action_switch_tab(self, tab_id: str) -> None:
        """Switch to the specified tab."""
        tabbed_content = self.query_one(TabbedContent)
        tabbed_content.active = tab_id


def run_cli(datasources: list[DataSource]) -> None:
    """Run the CLI application.

    Args:
        datasources: List of DataSource objects to load
    """
    app = DatasetChatbotApp(datasources)
    app.run()


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Dataset Chatbot CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "csv_files",
        nargs="*",
        type=Path,
        metavar="CSV_FILE",
        help="CSV files to load",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run with demo data (creates sample CSV files)",
    )

    args = parser.parse_args()

    if args.demo:
        import tempfile

        demo_dir = Path(tempfile.mkdtemp())

        sales_csv = demo_dir / "sales.csv"
        sales_csv.write_text(
            "date,product,quantity,price,region\n"
            "2024-01-01,Widget A,100,29.99,North\n"
            "2024-01-02,Widget B,50,49.99,South\n"
            "2024-01-03,Widget C,75,19.99,East\n"
            "2024-01-04,Widget A,120,29.99,West\n"
            "2024-01-05,Widget B,80,49.99,North\n"
        )

        customers_csv = demo_dir / "customers.csv"
        customers_csv.write_text(
            "customer_id,name,email,signup_date,tier\n"
            "1,John Doe,john@example.com,2023-06-15,Gold\n"
            "2,Jane Smith,jane@example.com,2023-08-20,Silver\n"
            "3,Bob Wilson,bob@example.com,2023-09-10,Bronze\n"
            "4,Alice Brown,alice@example.com,2023-10-05,Gold\n"
        )

        csv_files = [sales_csv, customers_csv]
        print(f"Created demo CSV files in {demo_dir}")
    else:
        csv_files = args.csv_files

    if not csv_files:
        print(
            "No CSV files provided. Use --demo for demo mode or provide CSV file paths."
        )
        sys.exit(1)

    valid_files = []
    for f in csv_files:
        if f.exists() and f.suffix.lower() == ".csv":
            valid_files.append(f)
        else:
            print(f"Warning: Skipping invalid file: {f}")

    if not valid_files:
        print("No valid CSV files found.")
        sys.exit(1)

    datasources = load_datasources(valid_files)

    if not datasources:
        print("No valid data sources could be loaded.")
        sys.exit(1)

    print(f"Loaded {len(datasources)} data source(s):")
    for ds in datasources:
        print(f"  - {ds.name}: {ds.row_count} rows, {len(ds.columns)} columns")
    print()

    run_cli(datasources)
