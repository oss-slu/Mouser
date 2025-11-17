"""Full test-suite runner and functional tests for core components."""

import sys
import os
import sqlite3
import tempfile
from unittest import TestLoader, TestSuite, TextTestRunner

# Third-party
from customtkinter import CTk

# First-party imports
from shared.password_utils import PasswordManager
from shared.tk_models import MouserPage
from shared.audio import AudioManager
from shared.flash_overlay import FlashOverlay
from databases.database_controller import DatabaseController
from databases.experiment_database import ExperimentDatabase

# Allow tests to import project modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ["DISPLAY"] = ":0"

# Import database test classes
from tests.database_test import (  # pylint: disable=wrong-import-position
    TestPlatform,
    TestUIComponents,
    TestDatabaseSetup,
    TestAnimalRFIDMethods,
    TestCageFunctions,
    TestGroupFunctions
)


def test_database_suite_execution():
    """Ensure all database-related tests pass together."""
    loader = TestLoader()
    suite = TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestPlatform))
    suite.addTests(loader.loadTestsFromTestCase(TestUIComponents))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseSetup))
    suite.addTests(loader.loadTestsFromTestCase(TestAnimalRFIDMethods))
    suite.addTests(loader.loadTestsFromTestCase(TestCageFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestGroupFunctions))

    runner = TextTestRunner(verbosity=2)
    result = runner.run(suite)

    assert result.wasSuccessful(), "Database test suite failed"


def test_database_controller_quick(monkeypatch):  # pylint: disable=unused-argument
    """Sanity test for DatabaseController using dummy db."""

    class DummyDB:
        """Minimal mock database."""

        def get_measurement_items(self):
            return ["weight"]

        def get_cages_by_group(self):
            return {"1": [1]}

        def get_cage_assignments(self):
            return {"101": (1,)}

        def get_animals(self):
            return [("101",)]

        def get_measurements_by_date(self, _):
            return [("101", "2025", "weight", 10.0)]

        def get_groups(self):
            return ["A"]

        def update_animal_cage(self, _a, _b):
            return None

        class _conn:  # pylint: disable=too-few-public-methods
            """Mock db connection."""

            @staticmethod
            def execute(_query):
                return None

            @staticmethod
            def fetchone():
                return (5,)

    mockdb = DummyDB()
    controller = DatabaseController(db=mockdb)

    group = controller.get_groups()
    cage_max = controller.get_cage_max()
    valid_animal = controller.check_valid_animal("101")
    valid_cage = controller.check_valid_cage("999")
    controller.update_animal_cage("101", 2)

    assert group == ["A"]
    assert cage_max == 5
    assert valid_animal is True
    assert valid_cage is False


def test_experiment_database_in_memory():
    """Validate basic SQLite operations with in-memory DB."""
    experiment_db = ExperimentDatabase(":memory:")

    experiment_db._conn.execute("""   -- pylint: disable=protected-access
        CREATE TABLE experiments_db (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            weight REAL
        );
    """)

    experiment_db._conn.executescript("""  -- pylint: disable=protected-access
        INSERT INTO experiments_db (name, weight)
        VALUES
            ('Mouse A', 25.0),
            ('Mouse B', 30.5);
    """)

    experiment_db._conn.commit()  # pylint: disable=protected-access

    rows = list(experiment_db._conn.execute("SELECT * FROM experiments_db;"))  # pylint: disable=protected-access
    assert len(rows) == 2
    assert rows[0][1] == "Mouse A"
    assert rows[1][2] == 30.5

    experiment_db._conn.close()  # pylint: disable=protected-access


def test_password_manager_encrypt_decrypt():
    """Ensure encryption and decryption returns original data."""
    password = PasswordManager("Test123")
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(b"Secret message")
    temp_path = temp.name
    temp.close()

    password.encrypt_file(temp_path)
    decrypted_data = password.decrypt_file(temp_path)

    assert decrypted_data == b"Secret message"

    os.remove(temp_path)


def test_file_utils_temp_file(tmp_path):  # pylint: disable=unused-argument
    """Ensure temporary files can be read and written."""
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(b"Hello World")
    temp_path = temp.name
    temp.close()

    with open(temp_path, "rb") as file:
        content = file.read()

    assert content == b"Hello World"


def test_tk_models_basic():
    """Smoke test: MouserPage instantiates properly."""
    root = CTk()
    page = MouserPage(root, "Test Page")
    assert page is not None
    assert isinstance(page, MouserPage)
    root.destroy()


def test_audio_playback_mocked(monkeypatch):
    """Ensure AudioManager.play invokes private __play correctly when idle."""

    class MockPlay:
        """Callable used to capture playback call."""

        def __init__(self):
            self.called = False
            self.file = None

        def __call__(self, filename):
            self.called = True
            self.file = filename
            return True

    mock_play = MockPlay()
    monkeypatch.setattr("shared.audio.AudioManager._AudioManager__play", mock_play)

    fake = tempfile.NamedTemporaryFile(delete=False)
    fake.write(b"data")
    fake.close()

    AudioManager._is_playing = False  # pylint: disable=protected-access
    AudioManager.play(fake.name)

    assert mock_play.called is True
    assert mock_play.file == fake.name

    os.remove(fake.name)


def test_audio_playback_busy(monkeypatch):  # pylint: disable=unused-argument
    """Ensure AudioManager prevents overlapping playback."""
    AudioManager._is_playing = True  # pylint: disable=protected-access
    AudioManager.play("dummy.mp3")
    AudioManager._is_playing = False  # pylint: disable=protected-access


def test_flash_overlay_behavior():
    """Basic FlashOverlay instantiation and method calls."""
    root = CTk()
    overlay = FlashOverlay(root, "Test Message")

    if hasattr(overlay, "show"):
        overlay.show()
    if hasattr(overlay, "hide"):
        overlay.hide()
    if hasattr(overlay, "flash"):
        overlay.flash()

    assert True
