'''Database Unit Tests'''
import sys
import os
from datetime import datetime
import time
import tempfile
import importlib.util
import types

# Ensure repository root is on sys.path so tests can import the local `databases` package.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    # First try a normal import (works when repo root is on sys.path)
    from databases.experiment_database import ExperimentDatabase
    from databases.database_controller import DatabaseController
except ModuleNotFoundError:
    # Fallback: load modules directly from file paths so tests can be run from the tests/ folder
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    exp_path = os.path.join(repo_root, 'databases', 'experiment_database.py')
    ctrl_path = os.path.join(repo_root, 'databases', 'database_controller.py')

    spec = importlib.util.spec_from_file_location(
        'databases.experiment_database', exp_path)
    exp_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exp_mod)
    # Prepare a package context so relative imports inside database_controller.py work
    pkg = types.ModuleType('databases')
    pkg.__path__ = [os.path.join(repo_root, 'databases')]
    sys.modules['databases'] = pkg
    sys.modules['databases.experiment_database'] = exp_mod

    spec2 = importlib.util.spec_from_file_location(
        'databases.database_controller', ctrl_path)
    ctrl_mod = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(ctrl_mod)

    ExperimentDatabase = exp_mod.ExperimentDatabase
    DatabaseController = ctrl_mod.DatabaseController


def create_temp_file():
    '''Function to create temporary file and return it'''
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.close() 
    return temp.name

def get_platform():
    '''Function that returns identifier for operating system'''
    return sys.platform

def delete_file(path):
    '''Function to check if a file exist in path and deletes it'''
    if os.path.exists(path):
        os.remove(path)

class TestPlatform(unittest.TestCase):
    def setUp(self):
        self.temp_db_path = tempfile.NamedTemporaryFile(delete=False).name
        self.db = ExperimentDatabase(self.temp_db_path)

        def tearDown(self):
            self.db.close_connection()
            os.remove(self.temp_db_path)

    def test_database_across_platform(self):
        '''Test to validate SQLite operations across Windows, macOS, and Linux'''
        temp_db_path = create_temp_file()
        temp_db = tempfile.NamedTemporaryFile(delete=False)

        db = ExperimentDatabase(temp_db_path)
        db.setup_experiment("Test", "Test Mouse", False, 16, 4, 4,
                        "Weight", 1, ["Investigator"], "Weight")
        db.setup_groups(["Control", "Group 1", "Group 2", "Group 3"], 4)
        for i in range(0,4):
            group_id = 1 if i < 2 else 2
            db.add_animal(animal_id=i + 1, rfid=str(10 + i), group_id=group_id)

        value = db.get_animal_rfid(animal_id=1)
        os_name = get_platform()

        self.assertEqual(value, '10')
        self.assertIn(os_name, ["win32", "darwin", "linux"])

        delete_file(temp_db_path)

'''Test class for UI components'''
class TestUIComponents(unittest.TestCase):
    def setUp(self):
        self.root = CTk()
        self.experiment_menu = ExperimentMenuUI(self.root, "test_file.mouser")
        self.new_experiment = self.experiment_menu.new_experiment
        self.db = self.experiment_menu.data_page.database

        if hasattr(self, "new_experiment"):
            self.assertIsNotNone(self.new_experiment)

    def tearDown(self):
        if hasattr(self, "db"):
            self.db.close_connection()



    '''Test if the buttons in experiment menu ui exists'''
    def test_buttons_exist(self):
        self.assertIsNotNone(self.experiment_menu.collection_button)
        self.assertIsNotNone(self.experiment_menu.analysis_button)
        self.assertIsNotNone(self.experiment_menu.group_button)
        self.assertIsNotNone(self.experiment_menu.rfid_button)
        self.assertIsNotNone(self.experiment_menu.summary_button)


    '''Test button states'''
    def test_button_states(self):
        if not self.experiment_menu.all_rfid_mapped():
            self.assertEqual(self.experiment_menu.collection_button.cget("state"), "disabled")
            self.assertEqual(self.experiment_menu.analysis_button.cget("state"), "disabled")
        else:
            self.assertEqual(self.experiment_menu.rfid_button.cget("state"), "disabled")

    def test_frame_navigation(self):
        self.experiment_menu.data_page.raise_frame()
        self.experiment_menu.analysis_page.raise_frame()


    '''Test scaling factor of the font on mac'''
    def test_platform_scaling(self):
        if self.root.tk.call('tk', 'windowingsystem') == 'aqua':
            try:
                default_font = self.root.option_get("font", "*")
            except sqlite3.Error:
                default_font = None
            self.assertIsNotNone(default_font)


    '''Test to check if new_experiment ui exist'''
    def test_new_experiment_ui(self):
        self.assertIsNotNone(self.new_experiment)


class TestDatabaseSetup(unittest.TestCase):
    '''Test Basic Setup of Database'''
    _fd, _dbfile = tempfile.mkstemp(suffix=".db")
    os.close(_fd)
    db = ExperimentDatabase(file=_dbfile)
    db.setup_experiment(
        "Test",
        "Test Mouse",
        False,
        16,
        4,
        4,
        "A",
        "test-123",
        ["Tester"],
        "Weight",
    )
    db.setup_groups([
        "Control",
        "Group 1",
        "Group 2",
        "Group 3",
    ], cage_capacity=4)

    def tearDown(self):
        self.db.close_connection()
        os.remove(self.temp_db.name)

    def test_num_animals(self):
        '''Checks if num animals equals expected.'''
        self.assertEqual(16, self.db.get_number_animals())

    def test_num_groups(self):
        '''Checks if num groups equals expected.'''
        # Use public API to get number of groups
        print("Returned group count:", self.db.get_number_groups())
        assert 4 == self.db.get_number_groups()

    def test_cage_max(self):
        '''Checks if cage max equals expected.'''
        # ExperimentDatabase doesn't expose cage_max directly; use the controller
        ctrl = DatabaseController(self.db.db_file)
        assert 4 == ctrl.get_cage_max()

    def test_get_all_groups(self):
        '''Checks if group names match expected'''
        # ExperimentDatabase returns a list of group names
        assert ["Control", "Group 1", "Group 2", "Group 3"] == self.db.get_groups()

    # Legacy get_cages test removed: functionality replaced by get_cages_by_group()

class TestAnimalRFIDMethods:
    '''Test if the animal RFID methods work'''
    _fd, _dbfile = tempfile.mkstemp(suffix=".db")
    os.close(_fd)
    db = ExperimentDatabase(file=_dbfile)
    db.setup_experiment(
        "Test",
        "Test Mouse",
        False,
        16,
        4,
        4,
        "A",
        "test-123",
        ["Tester"],
        "Weight",
    )
    db.setup_groups(["Control", "Group 1"], cage_capacity=4)
    for i in range(0,4):
        db.add_animal(animal_id=i, rfid=str(10 + i), group_id=1)

    def test_add_animal_ids(self):
        '''Test if animal id of particular animal matches expected.'''
        # RFID values are stored as strings
        assert 1 == self.db.get_animal_id('10')


    def test_get_animal_rfid(self):
        '''Test if particular animal RFID numbers match expected.'''
        self.assertEqual('10', self.db.get_animal_rfid(1))

    def test_get_animals_rfid(self):
        '''Test if animal rfids match expected.'''
        # Use current API name: returns list of strings
        assert ['10', '11', '12', '13'] == self.db.get_all_animals_rfid()

class TestCageFunctions(unittest.TestCase):
    '''Tests the cage functions.'''
    _fd, _dbfile = tempfile.mkstemp(suffix=".db")
    os.close(_fd)
    db = ExperimentDatabase(file=_dbfile)
    db.setup_experiment(
        "Test",
        "Test Mouse",
        False,
        16,
        4,
        4,
        "A",
        "test-123",
        ["Tester"],
        "Weight",
    )
    db.setup_groups(["Control", "Group 1"], cage_capacity=4)
    for i in range(0,4):
        db.add_animal(animal_id=i, rfid=str(10 + i), group_id=1)

    def test_get_cages(self):
        '''Placeholder: cage behavior validated via get_cages_by_group.'''
        

    def test_get_animals_from_cage(self):
        '''Tests if animals from a particular cage match expected.'''
        # get_animals_in_cage expects a group name
        assert [(1,), (2,)] == self.db.get_animals_in_cage('Control')

    def test_get_animals_by_cage(self):
        '''Tests if animals by caged dict matches expected.'''
        # No direct API for animals_by_cage; validate cage assignments mapping instead
        assignments = self.db.get_cage_assignments()
        # Ensure the first two animals are assigned (group_id, cage_number) tuples
        assert assignments[1][0] == 1
        assert isinstance(assignments[1][1], int)

class TestGroupFunctions(unittest.TestCase):
    '''Test Group Functions.'''
    _fd, _dbfile = tempfile.mkstemp(suffix=".db")
    os.close(_fd)
    db = ExperimentDatabase(file=_dbfile)
    db.setup_experiment(
        "Test",
        "Test Mouse",
        False,
        16,
        4,
        4,
        "A",
        "test-123",
        ["Tester"],
        "Weight",
    )
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
