"""Tests for application save behavior on exit."""

import os
import sys

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from databases.experiment_database import ExperimentDatabase
from shared import file_utils
from ui.commands import global_state, save_and_close


class DummyRoot:
    """Minimal root-like object for close callback tests."""

    def __init__(self):
        self.destroy_called = False

    def destroy(self):
        self.destroy_called = True


@pytest.fixture(autouse=True)
def cleanup_state():
    """Reset singleton DB instances and command global state."""
    prior_state = global_state.copy()
    ExperimentDatabase._instances.clear()  # pylint: disable=protected-access
    yield
    for db in list(ExperimentDatabase._instances.values()):  # pylint: disable=protected-access
        db.close()
    ExperimentDatabase._instances.clear()  # pylint: disable=protected-access
    global_state.clear()
    global_state.update(prior_state)


def test_save_and_close_persists_temp_changes_to_original(tmp_path):
    """Closing app should copy temp DB updates back to original file."""
    original_path = tmp_path / "experiment.mouser"

    db = ExperimentDatabase(str(original_path))
    db.setup_experiment(
        "Exit Save",
        "Mouse",
        False,
        4,
        1,
        4,
        0,
        "exit-save-id",
        ["Dr. A"],
        "Weight",
    )
    db.close()

    temp_path = file_utils.create_temp_copy(str(original_path))
    temp_db = ExperimentDatabase(temp_path)
    temp_db.update_investigators(["Dr. A", "Dr. B"])

    global_state["current_file_path"] = str(original_path)
    global_state["temp_file_path"] = temp_path
    global_state["password"] = None

    root = DummyRoot()
    save_and_close(root)

    assert root.destroy_called

    saved_db = ExperimentDatabase(str(original_path))
    assert saved_db.get_investigators() == ["Dr. A", "Dr. B"]
    saved_db.close()


def test_save_and_close_without_active_file_still_closes():
    """Closing app should still close root when no file is active."""
    global_state["current_file_path"] = None
    global_state["temp_file_path"] = None
    global_state["password"] = None

    root = DummyRoot()
    save_and_close(root)

    assert root.destroy_called
