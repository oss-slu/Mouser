"""Tests for Investigator page display and add behavior."""

import os
import sys

import pytest
from customtkinter import CTk

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from databases.experiment_database import ExperimentDatabase
from experiment_pages.experiment.experiment_invest_ui import InvestigatorsUI


@pytest.fixture(autouse=True)
def cleanup_database_instances():
    """Reset DB singletons for test isolation."""
    ExperimentDatabase._instances.clear()  # pylint: disable=protected-access
    yield
    for db in list(ExperimentDatabase._instances.values()):  # pylint: disable=protected-access
        db.close()
    ExperimentDatabase._instances.clear()  # pylint: disable=protected-access


@pytest.fixture(scope="module")
def tk_root():
    """Create one Tk root for all tests, skip suite if Tk is unavailable."""
    try:
        root = CTk()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        pytest.skip(f"Tk unavailable for UI tests: {exc}")
    root.withdraw()
    yield root
    root.destroy()


def _displayed_investigators(page: InvestigatorsUI) -> list[str]:
    names: list[str] = []
    for row in page.list_frame.winfo_children():
        text = None
        if hasattr(row, "cget"):
            try:
                text = row.cget("text")
            except ValueError:
                text = None
        if text and text != "No investigators added yet.":
            names.append(text)
            continue

        for child in row.winfo_children():
            if not hasattr(child, "cget"):
                continue
            child_text = child.cget("text")
            if child_text and child_text != "Remove":
                names.append(child_text)
    return names


def _textbox_investigators(page: InvestigatorsUI) -> list[str]:
    return [
        line.strip()
        for line in page.investigator_textbox.get("1.0", "end-1c").splitlines()
        if line.strip() and line.strip() != "No investigators added yet."
    ]


def test_investigator_page_loads_existing_investigators(tmp_path, tk_root):
    """Page load should render currently persisted investigators."""
    db_path = tmp_path / "investigator_load.db"
    db = ExperimentDatabase(str(db_path))
    db.setup_experiment(
        "Load Test",
        "Mouse",
        False,
        2,
        1,
        2,
        0,
        "load-test",
        ["Dr. Smith", "Dr. Jones"],
        "Weight",
    )

    page = None
    try:
        page = InvestigatorsUI(tk_root, None, str(db_path))
        tk_root.update_idletasks()
        assert _displayed_investigators(page) == ["Dr. Smith", "Dr. Jones"]
        assert _textbox_investigators(page) == ["Dr. Smith", "Dr. Jones"]
    finally:
        if page is not None:
            page.destroy()


def test_add_investigator_updates_ui_and_persists_without_refresh(tmp_path, tk_root):
    """Add action should update in-memory UI list and backing storage immediately."""
    db_path = tmp_path / "investigator_add.db"
    db = ExperimentDatabase(str(db_path))
    db.setup_experiment(
        "Add Test",
        "Mouse",
        False,
        2,
        1,
        2,
        0,
        "add-test",
        ["Dr. Smith"],
        "Weight",
    )

    page = None
    try:
        page = InvestigatorsUI(tk_root, None, str(db_path))
        page.input_entry.insert(0, "Dr. Brown")
        page.add_investigator()
        tk_root.update_idletasks()

        assert _displayed_investigators(page) == ["Dr. Smith", "Dr. Brown"]
        assert _textbox_investigators(page) == ["Dr. Smith", "Dr. Brown"]
        assert page.db.get_investigators() == ["Dr. Smith", "Dr. Brown"]
    finally:
        if page is not None:
            page.destroy()
