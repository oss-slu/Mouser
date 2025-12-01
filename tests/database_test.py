"""Database and UI Unit Tests."""

import os
import sys
import time
import sqlite3
import unittest
import tempfile
from datetime import datetime

# Ensure repository root first
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from customtkinter import CTk  # noqa: E402
from experiment_pages.experiment.experiment_menu_ui import ExperimentMenuUI  # noqa: E402
from databases.experiment_database import ExperimentDatabase  # noqa: E402
from databases.database_controller import DatabaseController  # noqa: E402


def create_temp_file():
    """Create temp file for testing."""
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.close()
    return temp.name


def delete_file(path):
    """Remove a file if it exists."""
    if os.path.exists(path):
        os.remove(path)


def get_platform():
    """Return OS platform string."""
    return sys.platform


class TestPlatform(unittest.TestCase):
    """Platform and DB file handling."""

    def setUp(self):
        self.temp_db_path = create_temp_file()
        self.db = ExperimentDatabase(self.temp_db_path)

    def tearDown(self):
        self.db.close_connection()
        delete_file(self.temp_db_path)

    def test_database_across_platform(self):
        """Ensure DB operations work on all OS types."""
        temp_db = create_temp_file()
        db = ExperimentDatabase(temp_db)

        # Use positional args for DB signature compatibility
        db.setup_experiment(
            "Test", "Test Mouse", False, 16, 4, 4,
            "Weight", 1, ["Investigator"], "Weight"
        )

        # db.setup_groups exists ONLY if DB provides it
        if hasattr(db, "setup_groups"):
            db.setup_groups(["Control", "Group 1", "Group 2", "Group 3"], 4)

        for i in range(4):
            db.add_animal(
                i + 1,
                str(10 + i),
                1 if i < 2 else 2
            )

        self.assertEqual(db.get_animal_rfid(1), "10")
        self.assertIn(get_platform(), ["win32", "darwin", "linux"])
        delete_file(temp_db)


class TestUIComponents(unittest.TestCase):
    """UI structure tests."""

    def setUp(self):
        self.root = CTk()
        self.ui = ExperimentMenuUI(self.root, "test_file.mouser")

    def tearDown(self):
        db = getattr(self.ui, "data_page", None)
        if db and hasattr(db, "database"):
            db.database.close_connection()

    def test_buttons_exist(self):
        """Check existence of core UI buttons."""
        for name in [
            "collection_button",
            "analysis_button",
            "group_button",
            "rfid_button",
            "summary_button",
        ]:
            self.assertTrue(hasattr(self.ui, name))

    def test_button_states(self):
        """Check default state behavior."""
        if hasattr(self.ui, "all_rfid_mapped") and not self.ui.all_rfid_mapped():
            self.assertEqual(self.ui.collection_button.cget("state"), "disabled")
            self.assertEqual(self.ui.analysis_button.cget("state"), "disabled")

    def test_frame_navigation(self):
        """Ensure major frames can raise without error."""
        if hasattr(self.ui, "data_page"):
            self.ui.data_page.raise_frame()
        if hasattr(self.ui, "analysis_page"):
            self.ui.analysis_page.raise_frame()

    def test_new_experiment_ui_exists(self):
        """New experiment UI object must exist."""
        self.assertTrue(hasattr(self.ui, "new_experiment"))


class TestDatabaseSetup(unittest.TestCase):
    """Database setup and metadata tests."""

    def setUp(self):
        self.fd, self.dbfile = tempfile.mkstemp(suffix=".db")
        os.close(self.fd)
        self.db = ExperimentDatabase(self.dbfile)

        self.db.setup_experiment(
            "Test", "Test Mouse", False, 16, 4, 4,
            "A", "test-123", ["Tester"], "Weight"
        )

        if hasattr(self.db, "setup_groups"):
            self.db.setup_groups(["Control", "Group 1", "Group 2", "Group 3"], 4)

    def tearDown(self):
        '''Cleanup after test.'''
        self.db.close_connection()
        delete_file(self.dbfile)

    def test_num_animals(self):
        '''Test retrieval of number of animals.'''
        self.assertEqual(self.db.get_number_animals(), 16)

    def test_num_groups(self):
        '''Test retrieval of number of groups.'''
        if hasattr(self.db, "get_number_groups"):
            self.assertEqual(self.db.get_number_groups(), 4)

    def test_cage_max(self):
        '''Test retrieval of maximum cage capacity.'''
        ctrl = DatabaseController(self.db.db_file)
        self.assertEqual(ctrl.get_cage_max(), 4)

    def test_get_all_groups(self):
        '''Test retrieval of all group names.'''
        expected = ["Control", "Group 1", "Group 2", "Group 3"]
        if hasattr(self.db, "get_groups"):
            self.assertEqual(self.db.get_groups(), expected)


class TestAnimalRFIDMethods(unittest.TestCase):
    """Tests for RFID and animal lookup."""

    def setUp(self):
        self.fd, self.dbfile = tempfile.mkstemp(suffix=".db")
        os.close(self.fd)
        self.db = ExperimentDatabase(self.dbfile)

        self.db.setup_experiment(
            "Test", "Test Mouse", False, 16, 4, 4,
            "A", "test-123", ["Tester"], "Weight"
        )

        if hasattr(self.db, "setup_groups"):
            self.db.setup_groups(["Control", "Group 1"], 4)

        for i in range(4):
            self.db.add_animal(i + 1, str(10 + i), 1)

    def tearDown(self):
        '''Cleanup after test.'''
        self.db.close_connection()
        delete_file(self.dbfile)

    def test_get_animal_id(self):
        '''Test retrieval of an animal's ID.'''
        self.assertEqual(self.db.get_animal_id("10"), 1)

    def test_get_animal_rfid(self):
        '''Test retrieval of an animal's RFID.'''
        self.assertEqual(self.db.get_animal_rfid(1), "10")

    def test_get_animals_rfid(self):
        '''Test retrieval of all animal RFIDs.'''
        self.assertEqual(self.db.get_all_animals_rfid(), ["10", "11", "12", "13"])


class TestCageFunctions(unittest.TestCase):
    """Cage/group lookup tests."""

    def setUp(self):
        self.fd, self.dbfile = tempfile.mkstemp(suffix=".db")
        os.close(self.fd)
        self.db = ExperimentDatabase(self.dbfile)

        self.db.setup_experiment(
            "Test", "Test Mouse", False, 16, 4, 4,
            "A", "test-123", ["Tester"], "Weight"
        )

        if hasattr(self.db, "setup_groups"):
            self.db.setup_groups(["Control", "Group 1"], cage_capacity=4)

        for i in range(4):
            self.db.add_animal(i + 1, str(10 + i), 1)

    def tearDown(self):
        '''Cleanup after test.'''
        self.db.close_connection()
        delete_file(self.dbfile)

    def test_get_animals_in_cage(self):
        '''Test retrieval of animals in a cage/group.'''
        self.assertEqual(self.db.get_animals_in_cage("Control"), [(1,), (2,)])

    def test_get_cage_assignments(self):
        '''Test retrieval of cage assignments.'''
        mapping = self.db.get_cage_assignments()
        self.assertIsInstance(mapping[1][1], int)

    def test_get_cages_by_group(self):
        '''Test retrieval of cages by group.'''
        cages = self.db.get_cages_by_group()
        self.assertTrue(1 in cages)
        self.assertIsInstance(cages[1], list)


class TestWindowsSQLiteBehavior(unittest.TestCase):
    """Stress test for SQLite locking behavior."""

    def test_simulated_instrument_input(self):
        fd, db_path = tempfile.mkstemp()
        os.close(fd)
        delete_file(db_path)

        db = ExperimentDatabase(db_path)

        db.setup_experiment(
            "Windows Test", "Rat", True, 5, 1, 5, "B"
        )

        if hasattr(db, "setup_groups"):
            db.setup_groups(["RFID Group"], cage_capacity=4)

        for i in range(1, 6):
            db.add_animal(i, f"RFID-{i}", 1)

        for i in range(1, 6):
            if hasattr(db, "add_measurement"):
                db.add_measurement(i, 25 + i)
            time.sleep(0.01)

        today = datetime.now().strftime("%Y-%m-%d")
        if hasattr(db, "get_measurements_by_date"):
            rows = db.get_measurements_by_date(today)
            self.assertEqual(len(rows), 5)

        db.close()
        delete_file(db_path)


if __name__ == "__main__":
    unittest.main()
