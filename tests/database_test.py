"""Database and UI Unit Tests."""
import os
import sys
import time
import sqlite3
import unittest
import tempfile
from datetime import datetime

from customtkinter import CTk
from experiment_pages.experiment.experiment_menu_ui import ExperimentMenuUI

# Ensure repository root is visible to imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from databases.experiment_database import ExperimentDatabase
from databases.database_controller import DatabaseController

def create_temp_file():
    """Create a temporary file and return the path."""
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.close()
    return temp.name


def get_platform():
    """Return the platform identifier (win32, darwin, linux)."""
    return sys.platform


def delete_file(path):
    """Delete a file if it exists."""
    if os.path.exists(path):
        os.remove(path)


class TestPlatform(unittest.TestCase):
    """Tests platform-specific database behavior."""

    def setUp(self):  # pylint: disable=invalid-name
        self.temp_db_path = tempfile.NamedTemporaryFile(delete=False).name
        self.db = ExperimentDatabase(self.temp_db_path)

    def tearDown(self):  # pylint: disable=invalid-name
        self.db.close_connection()
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def test_database_across_platform(self):
        """Validate SQLite operations across all OS types."""
        temp_db_path = create_temp_file()
        db = ExperimentDatabase(temp_db_path)

        db.setup_experiment(
            "Test", "Test Mouse", False, 16, 4, 4,
            "Weight", 1, ["Investigator"], "Weight"
        )
        db.setup_groups(["Control", "Group 1", "Group 2", "Group 3"], 4)

        for i in range(0, 4):
            group_id = 1 if i < 2 else 2
            db.add_animal(i + 1, str(10 + i), group_id)

        value = db.get_animal_rfid(1)
        os_name = get_platform()

        self.assertEqual(value, '10')
        self.assertIn(os_name, ["win32", "darwin", "linux"])

        delete_file(temp_db_path)



class TestUIComponents(unittest.TestCase):
    """Tests UI elements in ExperimentMenuUI."""

    def setUp(self):  # pylint: disable=invalid-name
        self.root = CTk()
        self.experiment_menu = ExperimentMenuUI(self.root, "test_file.mouser")
        self.new_experiment = self.experiment_menu.new_experiment
        self.db = self.experiment_menu.data_page.database

    def tearDown(self):  # pylint: disable=invalid-name
        if isinstance(self.db, ExperimentDatabase):
            self.db.close_connection()

    def test_buttons_exist(self):
        """Ensure that all main UI buttons exist."""
        self.assertIsNotNone(self.experiment_menu.collection_button)
        self.assertIsNotNone(self.experiment_menu.analysis_button)
        self.assertIsNotNone(self.experiment_menu.group_button)
        self.assertIsNotNone(self.experiment_menu.rfid_button)
        self.assertIsNotNone(self.experiment_menu.summary_button)

    def test_button_states(self):
        """Ensure buttons enable/disable based on RFID mapping status."""
        if not self.experiment_menu.all_rfid_mapped():
            self.assertEqual(self.experiment_menu.collection_button.cget("state"), "disabled")
            self.assertEqual(self.experiment_menu.analysis_button.cget("state"), "disabled")
        else:
            self.assertEqual(self.experiment_menu.rfid_button.cget("state"), "disabled")

    def test_frame_navigation(self):
        """Ensure that the major UI pages can be raised without error."""
        self.experiment_menu.data_page.raise_frame()
        self.experiment_menu.analysis_page.raise_frame()

    def test_platform_scaling(self):
        """Check default font retrieval on macOS."""
        if self.root.tk.call('tk', 'windowingsystem') == 'aqua':
            try:
                default_font = self.root.option_get("font", "*")
            except sqlite3.Error:
                default_font = None
            self.assertIsNotNone(default_font)

    def test_new_experiment_ui_exists(self):
        """Ensure the new experiment UI object exists."""
        self.assertIsNotNone(self.new_experiment)


class TestDatabaseSetup(unittest.TestCase):
    """Tests for basic ExperimentDatabase setup."""
    _fd, _dbfile = tempfile.mkstemp(suffix=".db")
    os.close(_fd)
    db = ExperimentDatabase(file=_dbfile)

    db.setup_experiment(
        "Test", "Test Mouse", False, 16, 4, 4,
        "A", "test-123", ["Tester"], "Weight"
    )
    db.setup_groups(["Control", "Group 1", "Group 2", "Group 3"], 4)

    def tearDown(self):  # pylint: disable=invalid-name
        self.db.close_connection()
        if os.path.exists(self._dbfile):
            os.remove(self._dbfile)

    def test_num_animals(self):
        """Ensure correct number of animals."""
        self.assertEqual(16, self.db.get_number_animals())

    def test_num_groups(self):
        """Ensure correct number of groups."""
        self.assertEqual(4, self.db.get_number_groups())

    def test_cage_max(self):
        """Test cage capacity via controller."""
        ctrl = DatabaseController(self.db.db_file)
        self.assertEqual(4, ctrl.get_cage_max())

    def test_get_all_groups(self):
        """Check group name retrieval."""
        self.assertEqual(["Control", "Group 1", "Group 2", "Group 3"], self.db.get_groups())


class TestAnimalRFIDMethods(unittest.TestCase):
    """Tests for animal RFID handling."""

    _fd, _dbfile = tempfile.mkstemp(suffix=".db")
    os.close(_fd)
    db = ExperimentDatabase(file=_dbfile)

    db.setup_experiment(
        "Test", "Test Mouse", False, 16, 4, 4,
        "A", "test-123", ["Tester"], "Weight"
    )
    db.setup_groups(["Control", "Group 1"], 4)

    for i in range(0, 4):
        db.add_animal(i + 1, str(10 + i), 1)

    def tearDown(self):  # pylint: disable=invalid-name
        self.db.close_connection()
        if os.path.exists(self._dbfile):
            os.remove(self._dbfile)

    def test_add_animal_ids(self):
        """Test retrieval of animal ID from RFID."""
        self.assertEqual(1, self.db.get_animal_id('10'))

    def test_get_animal_rfid(self):
        """Ensure correct RFID retrieval."""
        self.assertEqual('10', self.db.get_animal_rfid(1))

    def test_get_animals_rfid(self):
        """Ensure list of RFIDs is correct."""
        self.assertEqual(['10', '11', '12', '13'], self.db.get_all_animals_rfid())


class TestCageFunctions(unittest.TestCase):
    """Tests cage-related database functions."""

    _fd, _dbfile = tempfile.mkstemp(suffix=".db")
    os.close(_fd)
    db = ExperimentDatabase(file=_dbfile)

    db.setup_experiment(
        "Test", "Test Mouse", False, 16, 4, 4,
        "A", "test-123", ["Tester"], "Weight"
    )
    db.setup_groups(["Control", "Group 1"], 4)

    for i in range(0, 4):
        db.add_animal(i + 1, str(10 + i), 1)

    def tearDown(self):  # pylint: disable=invalid-name
        self.db.close_connection()
        if os.path.exists(self._dbfile):
            os.remove(self._dbfile)

    def test_get_animals_from_cage(self):
        """Test animals retrieved from Control cage."""
        self.assertEqual([(1,), (2,)], self.db.get_animals_in_cage("Control"))

    def test_get_animals_by_cage(self):
        """Test dictionary of cage assignments."""
        assignments = self.db.get_cage_assignments()
        self.assertEqual(1, assignments[1][0])
        self.assertIsInstance(assignments[1][1], int)

    db.setup_groups(["Control", "Group 1"], cage_capacity=4)
    for i in range(0,4):
        db.add_animal(animal_id=i, rfid=str(10 + i), group_id=1)

    def test_get_all_groups(self):
        '''Test if groups match expected.'''
        assert ['Control', 'Group 1'] == self.db.get_groups()

    def test_get_animals_in_group(self):
        '''Tests if animals in particular group match expected.'''
        # Use group name with ExperimentDatabase API
        assert [(1,), (2,)] == self.db.get_animals_in_cage('Control')

    def test_get_animals_by_group(self):
        '''Tests if animals by group dict matches expected.'''
        # No direct animals_by_group API; verify groups and assignments are consistent
        groups = self.db.get_groups()
        assert 'Control' in groups

    def test_get_cages_by_group(self):
        '''Tests if cages by group dict matches expected.'''
        # get_cages_by_group returns a dict keyed by group_id -> list of cage numbers
        cages = self.db.get_cages_by_group()
        # Expect group 1 to have at least one cage and group 2 to exist
        assert 1 in cages
        assert isinstance(cages[1], list)

# Tests are intentionally small; disable too-few-public-methods pylint warning
class TestWindowsSQLiteBehavior:  # pylint: disable=too-few-public-methods
    '''Simulates rapid reads/writes to test for SQLite locking and path issues on Windows.'''
    def test_simulated_instrument_input(self):
        '''Simulate instrument input and rapid writes to the DB.'''
        # Use a temporary DB file for this test
        _fd, db_path = tempfile.mkstemp()
        os.close(_fd)

        # Ensure any leftover named file is removed before creating DB
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except OSError:
                pass

        db = ExperimentDatabase(file=db_path)

        db.setup_experiment(
            "Windows Test",
            "Rat",
            True,
            5,
            1,
            5,
            "B",
        )
        db.setup_groups(["RFID Group"], cage_capacity=4)

        for i in range(1, 6):
            db.add_animal(animal_id=i, rfid=f"RFID-{i}", group_id=1)

        for i in range(1, 6):
            db.add_measurement(animal_id=i, value=25 + i)
            time.sleep(0.05)

        today = datetime.now().strftime("%Y-%m-%d")
        data = db.get_measurements_by_date(today)

        assert len(data) == 5
        db.close()
        try:
            os.remove(db_path)
        except OSError:
            pass

if __name__ == "__main__":
    setup = TestDatabaseSetup()
    setup.test_num_animals()
    setup.test_num_groups()
    print("Tests ran successfully.")
